import argparse

def training_argsparser():
    # command line arguments
    parser = argparse.ArgumentParser()
    
    # training params
    parser.add_argument('--batch-size', '-b', type=int, 
                        help="training batch size", default=64)
    
    parser.add_argument('--epochs', '-e', type=int,
                        help="number of training epochs", default=100)

    parser.add_argument('--learning-rate', '-L', type=float,
                        help="learning rate for Adam optimizer",
                        default=0.004)

    parser.add_argument('--min-learning-rate', '-l', type=float,
                        help="min learning rate for Adam optimizer",
                        default=0.0001)
    
    parser.add_argument('--early-stopping-patience', type=int, 
                        help="patience value for early stopping callback", 
                        default=5)
    
    parser.add_argument('--early-stopping-min-delta', type=float, 
                        help="minimum change in the validation loss to "
                        "qualify as an improvement", default=1e-3)

    parser.add_argument('--reduce-lr-on-plateau-patience', type=int, 
                        help="patience value for ReduceLROnPlateau callback", 
                        default=2)

    parser.add_argument('--lr-reduction-factor', type=float, 
                        help="factor by which the learning rate will be "
                        "reduced", default=0.5)

    # model params
    # TODO - might want to yaml just the model params 
    # the arguments here are specific to BPNet
    parser.add_argument('--model-arch-name', type=str,
                        help="the name of the model architesture that will "
                        "be used in training (the name that will be used "
                        "to fetch the model from model_archs)",
                        default='BPNet')

    parser.add_argument('--sequence-generator-name', type=str,
                        help="the name of the sequence generator from "
                        "mseqgen library that will be used to generate "
                        "batches of data ", default='BPNet')

    parser.add_argument('--filters', '-f', type=int,
                        help="number of filters to use in BPNet",
                        default=64)

    parser.add_argument('--counts-loss-weight', '-w', type=float,
                        help="Weight for counts mse loss",
                        default=100.0)
    
    parser.add_argument('--control-smoothing', default=[[7.5, 80]])
    
    # parallelization params
    parser.add_argument('--threads', '-t', type=int,
                        help="number of parallel threads for batch "
                        "generation", default=10)
        
    parser.add_argument('--gpus', '-p', type=int,
                        help="number of gpus to use", default=1)
    
    # reference params
    parser.add_argument('--reference-genome', '-g', type=str, required=True,
                        help="number of gpus to use", default=1)
    
    parser.add_argument('--chrom-sizes', '-c', type=str, required=True,
                        help="path to chromosome sizes file")
    
    parser.add_argument('--chroms', nargs='+', required=True,
                        help="master list of chromosomes for the genome")
    
    parser.add_argument('--exclude-chroms', nargs='+', help="list of "
                        "chromosomes to be excluded", default=[])    

    # validation params
    parser.add_argument('--splits', '-s', type=str,
                        help="path to json file")

    # output params    
    parser.add_argument('--output-dir', '-d', type=str,
                        help="destination directory to store the model", 
                        default=".")
    
    parser.add_argument('--tag-length', type=int,
                        help="length of the alphanumeric tag for the model "
                        "file name (applies if --automate-filenames option "
                        "is used)", default=6)

    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping model "
                        "directories (applies if --automate-filenames "
                        "option is used)", default='US/Pacific')

    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the model output directory "
                        "and filename should be auto generated")

    parser.add_argument('--model-output-filename', type=str,
                        help="basename of the model file without the .h5 "
                        "extension (required if --automate-filenames is "
                        "not used)", default="")

    # batch gen parameters
    parser.add_argument('--input-seq-len', type=int, 
                        help="length of input DNA sequence", default=3088)

    parser.add_argument('--output-len', type=int, 
                        help="length of output profile", default=1000)

    parser.add_argument('--max-jitter', type=int, 
                        help="maximum value for randomized jitter to offset "
                        "the peaks from the exact center of the input",
                        default=128)

    parser.add_argument('--reverse-complement-augmentation', 
                        action='store_true', 
                        help="enable reverse complement augmentation")
    
    parser.add_argument('--negative-sampling-rate', type=float,
                        help="number of negatives to sample for every "
                        "positive peak", default=0.0)
        
    # input data params
    parser.add_argument('--input-data', '-i', type=str,
                        help="path to json file containing task information", 
                        required=True)
    
    parser.add_argument('--stranded', action='store_true', 
                        help="specify if the input data is stranded or "
                        "unstranded")

    parser.add_argument('--has-control', action='store_true', 
                        help="specify if the input data has controls")

    
    parser.add_argument('--sampling-mode', type=str, 
                        choices=['peaks', 'sequential', 'random'], 
                        default='peaks')
    
    parser.add_argument('--shuffle', action='store_true')
    
    # attribution prior params 
    parser.add_argument('--use-attribution-prior', action='store_true', 
                        help="specify if attribution prior loss model should "
                        "be used")
    
    parser.add_argument('--attribution-prior-frequency-limit', type=int, 
                        help="the maximum integer frequency index, k, to "
                        "consider for the attribution prior loss", default=150)

    parser.add_argument('--attribution-prior-limit-softness', type=float, 
                        help="amount to soften the "
                        "--attribution-prior-frequency-limit by", default=0.2)

    parser.add_argument('--attribution-prior-grad-smooth-sigma', type=int, 
                        help="amount to smooth the gradient before computing "
                        "the loss", default=3)
    
    parser.add_argument('--attribution-prior-profile-grad-loss-weight', 
                        type=float,  help="weight for the attribution "
                        "prior loss computed on profile gradients", 
                        default=200.0)

    parser.add_argument('--attribution-prior-counts-grad-loss-weight', 
                        type=float,  help="weight for the attribution "
                        "prior loss computed on counts gradients", 
                        default=100.0)

    return parser


def predict_argsparser():
    """ Command line arguments for the predict script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    # batch gen parameters
    parser.add_argument('--batch-size', '-b', type=int, help="test batch size",
                        default=64)
        
    parser.add_argument('--input-seq-len', type=int, 
                        help="length of input DNA sequence", default=3088)

    parser.add_argument('--output-len', type=int, 
                        help="length of output profile", default=1000)
    
    parser.add_argument('--sequence-generator-name', type=str,
                        help="the name of the sequence generator from "
                        "mseqgen library that will be used to generate "
                        "batches of data ", default='BPNet')

    # network params     
    parser.add_argument('--control-smoothing', default=[[7.5, 80]])
    
    # predict modes
    parser.add_argument('--predict-peaks', action='store_true', 
                        help="generate predictions only on the peaks "
                        "contained in the peaks.bed files")

    # reference params
    parser.add_argument('--reference-genome', '-g', type=str, required=True,
                        help="the path to the reference genome fasta file")
    
    parser.add_argument('--chrom-sizes', '-s', type=str, required=True,
                        help="path to chromosome sizes file")
    
    # input data params
    parser.add_argument('--chroms', '-c', nargs='+', required=True,
                        help="list of test chromosomes for prediction")
        
    parser.add_argument('--input-data', '-i', type=str,
                        help="path to json file containing task information", 
                        required=True)
    
    parser.add_argument('--stranded', action='store_true', 
                        help="specify if the input data is stranded or "
                        "unstranded (i.e in case --has-control is True)")

    parser.add_argument('--has-control', action='store_true', 
                        help="specify if the input data has controls")
    
    parser.add_argument('--model', '-m', type=str, 
                        help="path to the .h5 model file")

    parser.add_argument('--model-name', type=str,
                        help="the name of the model that will be used in "
                        "for predictions", default='BPNet')
    
    parser.add_argument('--model-dir', type=str,
                        help="directory where .h5 model files are stored")
    
    # output params
    parser.add_argument('--output-dir', '-o', type=str, required=True,
                        help="destination directory to store predictions as a "
                        "bigWig file")

    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the predictions output should "
                        "be stored in a timestamped subdirectory within "
                        "--output-dir")
    
    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping model "
                        "directories", default='US/Pacific')
    
    parser.add_argument('--exponentiate-counts', action='store_true', 
                        help="specify if the predicted counts should be "
                        "exponentiated before writing to the bigWig files")

    parser.add_argument('--output-window-size', type=int,
                        help="size of the central window of the output "
                        "profile predictions that will be written to the "
                        "bigWig files", default=1000)

    parser.add_argument('--other-tags', nargs='+',
                        help="list of additional tags to be added as "
                        "suffix to the filenames", default=[])

    # misc params
    parser.add_argument('--write-buffer-size', type=int,
                        help="size of the write buffer to store predictions "
                        "before writing to bigWig files", default=10000)
    return parser

def fastpredict_argsparser():
    """ Command line arguments for the predict script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    # batch gen parameters
    parser.add_argument('--batch-size', type=int, 
                        help="predict batch size", default=64)
        
    parser.add_argument('--threads', type=int,
                        help="number of parallel threads for batch generation",
                        default=10)
        
    parser.add_argument('--input-seq-len', type=int, 
                        help="length of input DNA sequence", default=2114)

    parser.add_argument('--output-len', type=int, 
                        help="length of output profile", default=1000)
    
    # predict modes
    parser.add_argument('--predict-peaks', action='store_true', 
                        help="generate predictions only on the peaks "
                        "contained in the .bed files from --input-data. "
                        "If not specified tiled genome wide predictions "
                        "are generated.")

    # reference params
    parser.add_argument('--reference-genome', type=str, required=True,
                        help="the path to the reference genome fasta file")
    
    parser.add_argument('--chrom-sizes', '-s', type=str, required=True,
                        help="path to chromosome sizes file")
    
    # input data params
    parser.add_argument('--chroms', nargs='+', required=True,
                        help="list of chromosomes for prediction")
        
    parser.add_argument('--input-data', type=str, required=True,
                        help="path to json file containing task information")
    
    parser.add_argument('--model', type=str, required=True,
                        help="path to the .h5 model file")
    
    parser.add_argument('--sequence_generator_name', type=str, required=True,
                        help="the name of the sequence generator in mseqgen "
                        "to use for batch generation")
    
    parser.add_argument('--stranded', action='store_true', 
                        help="specify if the input data is stranded or "
                        "unstranded")

    parser.add_argument('--has-control', action='store_true', 
                        help="specify if the input data has controls")
    
    # network params
    parser.add_argument('--control-smoothing', nargs='+',
                        help="sigma and window size for gaussian 1D smoothing "
                        "of second control track", default=[7.0, 81])

    # output params
    parser.add_argument('--output-window-size', type=int, required=True,
                        help="size of the central window of the output "
                        "profile predictions that will be written to the "
                        "HDF5/bigWig files (should be <= --output-len)")
    
    parser.add_argument('--output-dir', type=str, required=True,
                        help="destination directory to store predictions ")

    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping model "
                        "directories", default='US/Pacific')

    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the predictions output should "
                        "be stored in a timestamped subdirectory within "
                        "--output-dir")
    
    parser.add_argument('--generate-predicted-profile-bigWigs', 
                        action='store_true', 
                        help="generate bigWig files for predicted profile"
                        "tracks")
    
    return parser


def metrics_argsparser():
    """ Command line arguments for the metrics script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    # input params
    parser.add_argument('--profileA', '-A', type=str, required=True,
                        help="the bigWig with ground truth values or a "
                        "replicate")

    parser.add_argument('--profileB', '-B', type=str, required=True,
                        help="the bigWig with predicted values or the "
                        "second replicate")

    parser.add_argument('--smooth-profileA', nargs='+',
                        help="a list of two items, sigma and window width "
                        "for gaussian smoothing of profileA "
                        "before computing metrics. Empty list indicates no"
                        "smoothing", default=[])

    parser.add_argument('--smooth-profileB', nargs='+',
                        help="a list of two items, sigma and window width "
                        "for gaussian smoothing of profileB "
                        "before computing metrics. Empty list indicates no"
                        "smoothing", default=[])
    
    parser.add_argument('--countsA', type=str,
                        help="the bigWig with region counts assigned to "
                        "each base (the counts track that is produced by "
                        "the predict script). This is optional.")

    parser.add_argument('--countsB', type=str,
                        help="the bigWig with region counts assigned to "
                        "each base (the counts track that is produced by "
                        "the predict script). This is optional.")

    parser.add_argument('--apply-softmax-to-profileA', action='store_true',
                        help="apply softmax to profileA before computing"
                        "metrics (in casees where profileA is logits)")
    
    parser.add_argument('--apply-softmax-to-profileB', action='store_true',
                        help="apply softmax to profileB before computing"
                        "metrics (in casees where profileB is logits)")

    parser.add_argument('--metrics-seq-len', type=int, 
                        help="the length of the sequence over which to "
                        "compute the metrics", default=1000)
    
    parser.add_argument('--peaks', type=str, 
                        help="the path to the file containing ")
    
    parser.add_argument('--bounds-csv', type=str, 
                        help="the path to the file containing upper and"
                        "lower bounds for mnll, cross entropy, jsd,"
                        "pearson & spearman correlation")

    parser.add_argument('--step-size', type=int,
                        help="the step size for genome wide metrics", 
                        default=50)
    
    parser.add_argument('--chroms', '-c', nargs='+', required=True,
                        help="list of test chromosomes to compute metrics")
    
    parser.add_argument('--exclude-zero-profiles', action='store_true',
                        help="exclude observed or predicted profiles that "
                        "are all zeros")

    # output params
    parser.add_argument('--output-dir', '-o', type=str, required=True,
                        help="destination directory to store metrics results")
    
    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the metrics output should "
                        "be stored in a timestamped subdirectory within "
                        "--output-dir")

    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping output "
                        "directories", default='US/Pacific')
    
    parser.add_argument('--other-tags', nargs='+',
                        help="list of additional tags to be added as "
                        "suffix to the filenames", default=[])

    # reference params
    parser.add_argument('--chrom-sizes', '-s', type=str, required=True,
                        help="path to chromosome sizes file")
    return parser

def interpret_argsparser():
    """ Command line arguments for the interpret script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    #reference params
    parser.add_argument('--reference-genome', '-g', type=str, required=True,
                        help="path to the reference genome file")

    # input params
    parser.add_argument('--input-seq-len', type=int, required=True,
                        help="the length of the input sequence to the model")
    
    parser.add_argument('--control-len', type=int, required=True,
                        help="the length of the control input to the model")

    parser.add_argument('--model', '-m', type=str, required=True,
                        help="the path to the model (.h5) file")

    parser.add_argument('--task-id', '-t', type=int,
                        help="In the multitask case the integer sequence "
                        "number of the task for which the interpretation "
                        "scores should be computed. For single task use 0.",
                        default=0)
    
    parser.add_argument('--bed-file', '-b', type=str, required=True,
                        help="the path to the bed file containing "
                        "postions at which the model should be interpreted")

    parser.add_argument('--sample', '-s', type=int,
                        help="the number of samples to randomly sample from "
                        "the bed file. Only one of --sample or --chroms can "
                        "be used.")

    parser.add_argument('--chroms', '-c', nargs='+',
                        help="list of chroms on which the contribution scores "
                        "are to be computed. If not specified all chroms in "
                        "--bed-file will be processed.")

    parser.add_argument('--presort-bed-file', action='store_true', 
                        help="specify if the --bed-file should be sorted in "
                        "descending order of enrichment. It is assumed that "
                        "the --bed-file has 'signalValue' in column 7 to use "
                        "for sorting.")
    
    parser.add_argument('--control-info', type=str,
                        help="path to the input json file that has paths to "
                        "control bigWigs. The --task-id is matched with "
                        "'task_id' in the the json file to get the list of "
                        "control bigWigs")

    parser.add_argument('--control-smoothing', nargs='+',
                        help="sigma and window width for gaussian 1d "
                        "smoothing of the control", default=[7.0, 81])
    
    parser.add_argument('--num-shuffles', type=int,
                        help="the number of dinucleotide shuffles to perform "
                        "on each input sequence", default=20)   
    
    parser.add_argument('--gen-null-dist', action='store_true', 
                        help="generate null distribution of shap scores by "
                        "using a dinucleotide shuffled input sequence") 

    parser.add_argument('--seed', type=int,
                        help="seed to create a NumPy RandomState object used"
                        "for performing shuffles", default=20201208)  
    
    # output params
    parser.add_argument('--output-directory', '-o', type=str, required=True,
                        help="destination directory to store the "
                        "interpretation scores")
    
    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the interpret output should be stored"
                        "in a timestamped subdirectory within --output-dir")

    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping output "
                        "directories", default='US/Pacific')
    return parser


def shap_scores_argsparser():
    """ Command line arguments for the shap script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    #reference params
    parser.add_argument('--reference-genome', '-g', type=str, required=True,
                        help="path to the reference genome file")

    # input params
    parser.add_argument('--input-seq-len', type=int, required=True,
                        help="the length of the input sequence to the model")
    
    parser.add_argument('--control-len', type=int, required=True,
                        help="the length of the control input to the model")

    parser.add_argument('--model', '-m', type=str, required=True,
                        help="the path to the model (.h5) file")

    parser.add_argument('--task-id', '-t', type=int,
                        help="In the multitask case the integer sequence "
                        "number of the task for which the interpretation "
                        "scores should be computed. For single task use 0.",
                        default=0)
    
    parser.add_argument('--bed-file', '-b', type=str, required=True,
                        help="the path to the bed file containing "
                        "postions at which the model should be interpreted")

    parser.add_argument('--sample', '-s', type=int,
                        help="the number of samples to randomly sample from "
                        "the bed file. Only one of --sample or --chroms can "
                        "be used.")

    parser.add_argument('--chroms', '-c', nargs='+',
                        help="list of chroms on which the contribution scores "
                        "are to be computed. If not specified all chroms in "
                        "--bed-file will be processed.")

    parser.add_argument('--presort-bed-file', action='store_true', 
                        help="specify if the --bed-file should be sorted in "
                        "descending order of enrichment. It is assumed that "
                        "the --bed-file has 'signalValue' in column 7 to use "
                        "for sorting.")
    
    parser.add_argument('--control-info', type=str,
                        help="path to the input json file that has paths to "
                        "control bigWigs. The --task-id is matched with "
                        "'task_id' in the the json file to get the list of "
                        "control bigWigs")

    parser.add_argument('--control-smoothing', nargs='+',
                        help="sigma and window width for gaussian 1d "
                        "smoothing of the control", default=[7.0, 81])
    
    parser.add_argument('--num-shuffles', type=int,
                        help="the number of dinucleotide shuffles to perform "
                        "on each input sequence", default=20)   
    
    parser.add_argument('--gen-null-dist', action='store_true', 
                        help="generate null distribution of shap scores by "
                        "using a dinucleotide shuffled input sequence") 

    parser.add_argument('--seed', type=int,
                        help="seed to create a NumPy RandomState object used"
                        "for performing shuffles", default=20210304)  
    
    # output params
    parser.add_argument('--output-directory', '-o', type=str, required=True,
                        help="destination directory to store the "
                        "interpretation scores")
    
    parser.add_argument('--automate-filenames', action='store_true', 
                        help="specify if the interpret output should be stored"
                        "in a timestamped subdirectory within --output-dir")

    parser.add_argument('--time-zone', type=str,
                        help="time zone to use for timestamping output "
                        "directories", default='US/Pacific')
    return parser


def modisco_argsparser():
    """ Command line arguments for the run_modisco script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--scores-path", type=str, 
                        help="Path to the importance scores hdf5 file")
    
    parser.add_argument("--scores-locations", type=str, 
                        help="path to bed file containing the locations "
                        "that match the scores")

    parser.add_argument("--output-directory", type=str, 
                        help="Path to the output directory")
    
    
    return parser

def motif_discovery_argsparser():
    """ Command line arguments for the motif_discovery script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--scores-path", type=str, 
                        help="Path to the importance scores hdf5 file")
    
    parser.add_argument("--scores-locations", type=str, 
                        help="path to bed file containing the locations "
                        "that match the scores")

    parser.add_argument("--output-directory", type=str, 
                        help="Path to the output directory")
    
    parser.add_argument('--modisco-window-size', type=int,
                        help="size of the window around the peak "
                        "coodrinate that will be considered for motif"
                        "discovery", default=400)
    return parser

def embeddings_argsparser():
    """ Command line arguments for the embeddings script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--model', '-m', type=str, required=True,
                        help="the path to the model (.h5) file")
    
    parser.add_argument('--reference-genome', '-g', type=str, required=True,
                        help="number of gpus to use")
    
    parser.add_argument('--input-layer-name', type=str, 
                        help="name of the input sequence layer", 
                        default='sequence')

    parser.add_argument('--input-layer-shape', nargs='+', required=True,
                        type=int,
                        help="shape of the input sequence layer (specify"
                        "list of values and omit the batch(?) dimension)")
    
    parser.add_argument('--embeddings-layer-name', type=str, 
                        help="full name of layer for embeddings output. "
                        "Cannot be combined with "
                        "--numbered-embeddings-layers-prefix.")
    
    parser.add_argument('--cropped-size', type=int,
                        help="the size to which all embeddings outputs "
                        "should be cropped to")

    parser.add_argument('--numbered-embeddings-layers-prefix', type=str, 
                        help="common prefix string, of all required "
                        "layers, for matching. Cannot be "
                        "combined with --embeddings-layer-name")

    parser.add_argument('--num-numbered-embeddings-layers', type=int, 
                        help="number of embeddings layers with common prefix "
                        "specified by --numbered-embeddings-layers-prefix. ", 
                        default=8)

    parser.add_argument('--flatten-embeddings-layer',
                        action='store_true', 
                        help="specify if the embeddings layers should be"
                        "flattened")

    parser.add_argument('--peaks', type=str, required=True,
                        help="10 column bed narrowPeak file containing "
                        "chromosome positions to compute embeddings")
    
    parser.add_argument('--batch-size', type=int, 
                        help="batch size for processing the "
                        "chromosome positions", default=64)
        
    parser.add_argument('--output-directory', type=str,
                        help="output directory path", default='.')
    
    parser.add_argument('--output-filename', type=str,
                        help="name of compressed numpy file to store "
                        "the embeddings", default="embeddings.h5")
    
    
    return parser


def logits2profile_argsparser():
    """ Command line arguments for the logits2counts script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--logits-file', type=str, required=True,
                        help="Path to the logits bigWig file that was "
                             "generated by the predict script")
    
    parser.add_argument('--counts-file', type=str, required=True,
                        help="Path to the exponentiated counts bigWig file "
                             "that was generated by the predict script")

    parser.add_argument('--output-directory', type=str, required=True,
                        help="Path to the output directory")

    parser.add_argument('--output-filename', type=str, required=True,
                        help="output file name excluding extension")
    
    parser.add_argument('--peaks', type=str, required=True,
                        help="Path to the bed file containing the chromosome"
                             "coordinates at which the logits to counts "
                             "conversion should take place")
    
    parser.add_argument('--chroms', nargs='+', required=True,
                        help="list of chroms for the output bigWig header")
    
    parser.add_argument('--chrom-sizes', type=str, required=True,
                        help="Path to the chromosome sizes file")

    parser.add_argument('--window-size', type=int,
                        help="size of the window around the chromosome "
                        "coodrinate that will be considered for logits to "
                        "counts conversion", default=1000)
    
    return parser


def bounds_argsparser():
    """ Command line arguments for the bounds script

        Returns:
            argparse.ArgumentParser
    """
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input-profiles', nargs='+',
                        help="list of input bigWig profile", default=[])

    parser.add_argument('--output-names', nargs='+',
                        help="list of outputnames for the bounds output "
                        "corresponding to each of the input profiles", 
                        default=[]) 

    parser.add_argument('--output-directory', type=str, required=True,
                        help="Path to the output directory")

    parser.add_argument('--peaks', type=str, required=True,
                        help="Path to the bed file containing the chromosome "
                        "coordinates. The bed file should have at least "
                        "3 columns, the first 3 being 'chrom', 'start', "
                        "and 'end'")
    
    parser.add_argument('--peak-width', type=int,
                        help="the span of the peak to be considered for "
                        "bounds computation", default=1000)
    
    parser.add_argument('--chroms', '-c', nargs='+',
                        help="list of chromosomes to be considered from "
                        "peaks file")
        
    parser.add_argument('--smoothing-params', nargs='+',
                        help="sigma and window size for gaussian 1D smoothing "
                        "of 'observed' and 'predicted' profiles", 
                        default=[7.0, 81])

    return parser

def counts_loss_weight_argsparser():
    """ Command line arguments for the counts_loss_weight script

        Returns:
            argparse.ArgumentParser
    """

    parser = argparse.ArgumentParser()
        
    parser.add_argument('--input-data', '-i', type=str,
                        help="path to json file containing task information", 
                        required=True)
    
    parser.add_argument('--peak-width', type=int,
                        help="the span of the peak to be considered for "
                        "counts loss weight computation", default=1000)
    
    parser.add_argument('--alpha', '-a', type=float, default=1.0,
                        help="parameter to scale profile loss relative to "
                        "the counts loss. A value < 1.0 will upweight the "
                        "profile loss")
    
    parser.add_argument('--default', '-d', type=float, default=100.0,
                        help="default value to use in case there are "
                        "exceptions or problems during the execution of the "
                        "script")
    
    return parser
