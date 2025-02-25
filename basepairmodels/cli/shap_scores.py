import h5py
import json
import numpy as np
import pandas as pd
import pyBigWig
import pysam
import shap
import tensorflow as tf
import tensorflow_probability as tfp

from basepairmodels.cli.argparsers import shap_scores_argsparser
from basepairmodels.cli.bpnetutils import *
from basepairmodels.cli.exceptionhandler import NoTracebackException
from basepairmodels.cli.shaputils import *
from basepairmodels.cli.logger import *
from basepairmodels.cli.losses import MultichannelMultinomialNLL
from mseqgen.sequtils import one_hot_encode
from mseqgen.utils import gaussian1D_smoothing
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import CustomObjectScope


def save_scores(peaks_df, one_hot_sequences, hyp_shap_scores, output_fname):
    """
        Function to save shap scores to HDF5 file
        
        Args:
            peaks_df (pandas.Dataframe): a pandas dataframe that
                has 'chrom', 'start', & 'end' columns for chrom
                positions
                
            one_hot_sequences (numpy.ndarray): numpy array of shape
                N x sequence_length x 4

            hyp_shap_scores (numpy.ndarray): shap scores corresponding
                to the input sequences (hypothetical contributions);
                numpy array of shape N x sequence_length x 4
                
            output_fname (str): path to the output .h5 file
            
    """
    
    # get the chroms, starts and ends as lists
    coords_chrom = peaks_df['chrom'].values
    coords_start = peaks_df['start'].values
    coords_end = peaks_df['end'].values
    
    num_examples = peaks_df.shape[0]
    seq_len = one_hot_sequences.shape[1]
    
    # open the HDF% file for writing
    f = h5py.File(output_fname, "w")
    
    coords_chrom_dset = f.create_dataset(
        "coords_chrom", (num_examples,),
        dtype=h5py.string_dtype(encoding="ascii"), compression="gzip"
    )
    coords_chrom_dset[:] = coords_chrom
    
    coords_start_dset = f.create_dataset(
        "coords_start", (num_examples,), dtype=int, compression="gzip"
    )
    coords_start_dset[:] = coords_start
    
    coords_end_dset = f.create_dataset(
        "coords_end", (num_examples,), dtype=int, compression="gzip"
    )
    coords_end_dset[:] = coords_end
        
    hyp_scores_dset = f.create_dataset(
        "hyp_scores", (num_examples, seq_len, 4), compression="gzip"
    )
    hyp_scores_dset[:, :, :] = hyp_shap_scores

    input_seqs_dset = f.create_dataset(
        "input_seqs", (num_examples, seq_len, 4), compression="gzip"
    )
    input_seqs_dset[:, :, :] = one_hot_sequences
    
    f.close()
    
def shap_scores(args, shap_dir):
    # load the model
    model = load_model(args.model)
    
    # read all the peaks into a pandas dataframe
    peaks_df = pd.read_csv(args.bed_file, sep='\t', header=None, 
                           names=['chrom', 'st', 'end', 'name', 'score',
                                  'strand', 'signalValue', 'p', 'q', 'summit'])

    if args.chroms is not None:
        # keep only those rows corresponding to the required 
        # chromosomes
        peaks_df = peaks_df[peaks_df['chrom'].isin(args.chroms)]
           
    if args.sample is not None:
        # randomly sample rows
        logging.info("Sampling {} rows from {}".format(
            args.sample, args.bed_file))
        peaks_df = peaks_df.sample(n=args.sample, random_state=args.seed)
    
    if args.presort_bed_file:
        # sort the bed file in descending order of peak strength
        peaks_df = peaks_df.sort_values(['signalValue'], ascending=False)
    
    # reset index (if any of the above 3 filters have been applied, 
    # no harm if they haven't)
    peaks_df = peaks_df.reset_index(drop=True)
    
    # add new columns for start and stop based on 'summit' position
    peaks_df['start'] = peaks_df['st'] + peaks_df['summit'] - \
        (args.input_seq_len // 2)
    peaks_df['end'] = peaks_df['st'] + peaks_df['summit'] + \
        (args.input_seq_len // 2)
        
    # get final number of peaks
    num_peaks = peaks_df.shape[0]
    logging.info("#Peaks - {}".format(num_peaks))
    
    # reference file to fetch sequences
    logging.info("Opening reference file ...")
    #REFERENCE FILE HERE
    fasta_ref = pysam.FastaFile(args.reference_genome) 
        
    # if controls have been specified we to need open the control files
    # for reading
    control_bigWigs = []
    if args.control_info is not None:
        # load the control info json file
        with open(args.control_info, 'r') as inp_json:
            try:
                input_data = json.loads(inp_json.read())
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                raise NoTracebackException(
                    exc_type.__name__ + ' ' + str(exc_value))
               
        logging.info("Opening control bigWigs ...")
        # get the control bigWig for each task
        for task in input_data:
            if input_data[task]['task_id'] == args.task_id:
                if 'control' in input_data[task].keys():
                    control_bigWig_path = input_data[task]['control']
                    
                    # check if the file exists
                    if not os.path.exists(control_bigWig_path):
                        raise NoTracebackException(
                            "File {} does not exist".format(
                                control_bigWig_path))
                    
                    logging.info(control_bigWig_path)
                    
                    # open the bigWig and add the file object to the 
                    # list
                    control_bigWigs.append(pyBigWig.open(control_bigWig_path))

    # log of sum of counts of the control track
    # if multiple control files are specified this would be
    # log(sum(position_wise_sum_from_all_files))
    bias_counts_input = np.zeros((num_peaks, 1))

    # the control profile and the smoothed version of the control 
    # profile (1 + 1 = 2, always :) )
    # if multiple control files are specified, the control profile for
    # each sample would be position_wise_sum_from_all_files
    bias_profile_input = np.zeros((num_peaks, args.control_len, 2))
    
    ## IF NO CONTROL BIGWIGS ARE SPECIFIED THEN THE TWO NUMPY ARRAYS
    ## bias_counts_input AND bias_profile_input WILL REMAIN ZEROS
    
    # list to hold all the sequences for the peaks
    sequences = []
    
    # iterate through all the peaks
    for idx, row in peaks_df.iterrows():
        start = row['start']
        end = row['end']
        
        # fetch the reference sequence at the peak location
        try:
            #SEQUENCE IS OBTAINED HERE
            seq = fasta_ref.fetch(row['chrom'], start, end).upper()        
        except ValueError: # start/end out of range
            logging.warn("Unable to fetch reference sequence at peak: "
                         "{} {}-{}.".format(row['chrom'], start, end))
            
            # use string of N's as a substitute
            seq = 'N'*args.input_seq_len
            
        # check if we have the required length
        if len(seq) != args.input_seq_len:
            logging.warn("Reference genome doesn't have required sequence " 
                         "length ({}) at peak: {} {}-{}. Returned length {}. "
                         "Using all N's.".format(
                             args.input_seq_len, row['chrom'], start, end, 
                             len(seq)))
            
            # use string of N's as a substitute
            seq = 'N'*args.input_seq_len     
        #MODIFY SEQUENCE HERE
        # fetch control values
        if len(control_bigWigs) > 0:
            # a different start and end for controls since control_len
            # is usually not the same as input_seq_len
            start = row['st'] + row['summit'] - (args.control_len // 2)
            end =  row['st'] + row['summit'] + (args.control_len // 2)

            # read the values from the control bigWigs
            for i in range(len(control_bigWigs)):
                vals = np.nan_to_num(
                    control_bigWigs[i].values(row['chrom'], start, end))
                bias_counts_input[idx, 0] += np.sum(vals)
                bias_profile_input[idx, :, 0] += vals
            
            # we need to take the log of the sum of counts
            # we add 1 to avoid taking log of 0
            # same as mseqgen does while generating batches
            bias_counts_input[idx, 0] = np.log(bias_counts_input[idx, 0] + 1)
                         
            # compute the smoothed control profile
            sigma = float(args.control_smoothing[0])
            window_width = int(args.control_smoothing[1])
            bias_profile_input[idx, :, 1] = gaussian1D_smoothing(
                bias_profile_input[idx, :, 0], sigma, window_width)

        # append to the list of sequences
        sequences.append(seq)

    # if null distribution is requested
    null_sequences = []
    if args.gen_null_dist:
        logging.info("generating null sequences ...")
        rng = np.random.RandomState(args.seed)
        
        # iterate over sequences and get the dinucleotide shuffled
        # sequence for each of them
        for seq in sequences:
            # get a list of shuffled seqs. Since we are setting
            # num_shufs to 1, the returned list will be of size 1
            shuffled_seqs = dinuc_shuffle(seq, 1, rng)
            null_sequences.append(shuffled_seqs[0])
        
        # null sequences are now our actual sequences
        sequences = null_sequences[:]

    # one hot encode all the sequences
    X = one_hot_encode(sequences, args.input_seq_len)
    print("X shape", X.shape)
        
    # inline function to handle dinucleotide shuffling
    def data_func(model_inputs):
        rng = np.random.RandomState(args.seed)
        return [dinuc_shuffle(model_inputs[0], args.num_shuffles, rng)] + \
        [
            np.tile(
                np.zeros_like(model_inputs[i]),
                (args.num_shuffles,) + (len(model_inputs[i].shape) * (1,))
            ) for i in range(1, len(model_inputs))
        ]
    
    # shap explainer for the counts head
    profile_model_counts_explainer = shap.explainers.deep.TFDeepExplainer(
        ([model.input[0], model.input[1]], 
         tf.reduce_sum(model.outputs[1], axis=-1)),
        data_func, 
        combine_mult_and_diffref=combine_mult_and_diffref)

    # explainer for the profile head
    weightedsum_meannormed_logits = get_weightedsum_meannormed_logits(
        model, task_id=args.task_id, stranded=True)
    profile_model_profile_explainer = shap.explainers.deep.TFDeepExplainer(
        ([model.input[0], model.input[2]], weightedsum_meannormed_logits),
        data_func, 
        combine_mult_and_diffref=combine_mult_and_diffref)

    logging.info("Generating 'counts' shap scores")
    counts_shap_scores = profile_model_counts_explainer.shap_values(
        [X, bias_counts_input], progress_message=100)
    
    # save the dictionary in HDF5 formnat
    logging.info("Saving 'counts' scores")
    output_fname = '{}/counts_scores.h5'.format(shap_dir)
    
    # save the hyp shap scores, one hot sequences & chrom positions
    # to a HDF5 file
    save_scores(peaks_df, X, counts_shap_scores[0], output_fname)
    
    logging.info("Generating 'profile' shap scores")
    profile_shap_scores = profile_model_profile_explainer.shap_values(
        [X, bias_profile_input], progress_message=100)
    
    # save the dictionary in HDF5 formnat
    logging.info("Saving 'profile' scores")
    output_fname = '{}/profile_scores.h5'.format(shap_dir)

    # save the profile hyp shap scores, one hot sequences & chrom 
    # positions to a HDF5 file
    save_scores(peaks_df, X, profile_shap_scores[0], output_fname)
    
    # save the dataframe as a new .bed file 
    peaks_df.to_csv('{}/peaks_valid_scores.bed'.format(shap_dir), 
                           sep='\t', header=False, index=False)
    
    # write all the command line arguments to a json file
    config_file = '{}/config.json'.format(shap_dir)
    with open(config_file, 'w') as fp:
        config = vars(args)
        json.dump(config, fp)
        
        
def shap_scores_main():
    # disable eager execution so shap deep explainer wont break
    tf.compat.v1.disable_eager_execution()
    
    # parse the command line arguments
    parser = shap_scores_argsparser()
    args = parser.parse_args()
    
    # check if the output directory exists
    if not os.path.exists(args.output_directory):
        raise NoTracebackException(
            "Directory {} does not exist".format(args.output_directory))

    # check if the output directory is a directory path
    if not os.path.isdir(args.output_directory):
        raise NoTracebackException(
            "{} is not a directory".format(args.output_directory))
    
    # check if the reference genome file exists
    if not os.path.exists(args.reference_genome):
        raise NoTracebackException(
            "File {} does not exist".format(args.reference_genome))

    # check if the model file exists
    if not os.path.exists(args.model):
        raise NoTracebackException(
            "File {} does not exist".format(args.model))

    # check if the bed file exists
    if not os.path.exists(args.bed_file):
        raise NoTracebackException(
            "File {} does not exist".format(args.bed_file))
    
    # if controls are specified check if the control_info json exists
    if args.control_info is not None:
        if not os.path.exists(args.control_info):
            raise NoTracebackException(
                "Input data file {} does not exist".format(args.control_info))
            
    # check if both args.chroms and args.sample are specified, only
    # one of the two is allowed
    if args.chroms is not None and args.sample is not None:
        raise NoTracebackException(
            "Only one of [--chroms, --sample]  is allowed")
            
    if args.automate_filenames:
        # create a new directory using current date/time to store the
        # shapation scores
        date_time_str = local_datetime_str(args.time_zone)
        shap_scores_dir = '{}/{}'.format(args.output_directory, date_time_str)
        os.mkdir(shap_scores_dir)
    else:
        shap_scores_dir = args.output_directory    

    # filename to write debug logs
    logfname = "{}/shap_scores.log".format(shap_scores_dir)
    
    # set up the loggers
    init_logger(logfname)
    
    # shap
    logging.info("Loading {}".format(args.model))
    with CustomObjectScope({'MultichannelMultinomialNLL': 
                            MultichannelMultinomialNLL}):
            
        shap_scores(args, shap_scores_dir)

if __name__ == '__main__':
    shap_scores_main()
