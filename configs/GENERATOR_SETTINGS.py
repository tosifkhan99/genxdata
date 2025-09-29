MINIMUM_ROWS_ALLOWED = 100
STREAM_BATCH_SIZE = 100000
BATCH_SIZE = 1000000
BATCH_MODE = False
SHUFFLE = False
WRITE_OUTPUT = True
DEBUG = False
PERF_REPORT = False
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/generator.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Normal mode large-volume optimization
# If num_of_rows >= this threshold, normal mode will offload non-dependent columns
# to intermediate Parquet files during generation to reduce peak memory usage.
NORMAL_MODE_OFFLOAD_THRESHOLD_ROWS = 1000000
INTERMEDIATE_STORAGE_DIR = "./output/_intermediate"
INTERMEDIATE_STORAGE_FORMAT = "parquet"
