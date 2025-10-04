# 🧬 GenXData
A Complete synthetic data framework for generating realistic data for your applications.

## 🚀 Getting Started

### 📦 Installation

GenXData uses Poetry for dependency management, which provides better dependency resolution and virtual environment management.

#### **🎯 Recommended: Poetry Installation**

**Step 1**: Install Poetry (if not already installed)
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry
```

**Step 2**: Install project dependencies
```bash
# Install all dependencies (including dev dependencies)
poetry install

# Install only production dependencies
poetry install --only=main
```

**Step 3**: Activate the virtual environment
```bash
# Activate Poetry shell
poetry shell

# Or run commands with Poetry
poetry run python main.py --help
```

#### **📋 Alternative: Pip Installation**

If you prefer using pip:

```bash
# (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Verify CLI is available
python -m cli.main_cli --help
```

### 🛠️ Running the tool

**Step 1**: Create a configuration file. You can copy examples from the [examples](examples) directory, or create your own configs (refer to examples folder or visit documentation in [dev-docs](dev-docs) for more info).

**Step 2**: Run the script with your configuration:

**Using Poetry (Recommended):**
```bash
# Generate data with Poetry
poetry run python main.py generate path/to/your/config.yaml

# With verbose logging
poetry run python main.py -l DEBUG generate examples/by-strategy/random_number_range_example.yaml
```

**Using Direct Python:**
```bash
# Generate data directly
python main.py generate path/to/your/config.yaml

# With verbose logging
python main.py -l DEBUG generate examples/by-strategy/random_number_range_example.yaml
```

### 🔧 Development Setup

For contributors and developers:

```bash
# Clone the repository
git clone <repository-url>
cd GenXData

# Install with development dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run ruff check --fix .
```

### 💻 **CLI Interface**
GenXData includes a comprehensive command-line interface for managing generators and configurations. The CLI provides several commands to explore, create, and generate data efficiently.

#### **Installation**

**Using Poetry (Recommended):**
```bash
poetry install
poetry shell
```

**Using Pip:**
```bash
# (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python -m cli.main_cli --help
```

#### **Global Options**
- `--help`: Show help message and available commands

#### **Available Commands**

##### **1. List Generators**
Explore available generators with optional filtering and statistics:

```bash
# List all generators (175 total across 9 domains)
poetry run python -m cli.main_cli list-generators

# Filter generators by name pattern
poetry run python -m cli.main_cli list-generators --filter NAME

# Show comprehensive statistics
poetry run python -m cli.main_cli list-generators --show-stats

# Combine verbose logging with filtering
poetry run python -m cli.main_cli -l DEBUG list-generators --filter NAME
```

##### **2. Show Generator Details**
Get detailed information about a specific generator:

```bash
# Show details of a specific generator
poetry run python -m cli.main_cli show-generator PERSON_NAME

# Output includes strategy and parameters
poetry run python -m cli.main_cli show-generator EMAIL_PATTERN
```

##### **3. Find Generators by Strategy**
List all generators using a specific strategy:

```bash
# Find generators using RANDOM_NAME_STRATEGY
poetry run python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Find generators using RANDOM_DATE_RANGE_STRATEGY
poetry run python -m cli.main_cli by-strategy RANDOM_DATE_RANGE_STRATEGY
```

##### **4. Create Configuration Files**
Generate configuration files from generator mappings:

```bash
# Create config with generator mapping
poetry run python -m cli.main_cli create-config \
  --mapping "name:FULL_NAME,age:PERSON_AGE,email:EMAIL_PATTERN" \
  --output test_config.json \
  --rows 50

# Create config with custom metadata
poetry run python -m cli.main_cli create-config \
  --mapping "product:PRODUCT_NAME,price:PRODUCT_PRICE" \
  --output ecommerce_config.yaml \
  --rows 1000 \
  --name "Ecommerce Dataset" \
  --description "Product catalog data"

# Use a mapping file instead of command line
poetry run python -m cli.main_cli create-config \
  --mapping-file mapping.json \
  --output config.yaml \
  --rows 500
```

##### **5. Generate Domain Configurations**
Create example configurations for specific domains:

```bash
# Generate domain-specific configuration examples
poetry run python -m cli.main_cli create-domain-configs

# Creates configs in ./output/ for:
# - ecommerce, healthcare, education, transportation, iot_sensors, etc.
```

##### **6. Generate Data**
Generate data from configurations:

```bash
# Generate data from your configuration
poetry run python -m cli.main_cli generate config.json

# Generate from example configurations
poetry run python -m cli.main_cli generate examples/by-strategy/random_number_range_example.yaml

# Generate data with streaming
poetry run python -m cli.main_cli generate config.yaml --stream examples/stream_configs/amqp_example.yaml
```

##### **7. Show Statistics**
View generator and strategy statistics:

```bash
# Show detailed statistics
poetry run python -m cli.main_cli stats

# Includes totals, strategy and domain distribution, and available strategies
```

#### **Command Examples & Use Cases**

```bash
# Discover available generators
poetry run python -m cli.main_cli list-generators

# Find name-related generators
poetry run python -m cli.main_cli list-generators --filter NAME

# See all generators using a specific strategy
poetry run python -m cli.main_cli by-strategy RANDOM_NAME_STRATEGY

# Create a user profile dataset
poetry run python -m cli.main_cli create-config \
  --mapping "name:FULL_NAME,email:EMAIL_PATTERN,age:PERSON_AGE" \
  --output user_profiles.json \
  --rows 1000

# Generate the data
poetry run python -m cli.main_cli generate user_profiles.json

# Create all domain example configs
poetry run python -m cli.main_cli create-domain-configs

# Generate healthcare data
poetry run python -m cli.main_cli generate ./output/healthcare_config.yaml

# Generate ecommerce data
poetry run python -m cli.main_cli generate ./output/ecommerce_config.yaml
```

#### **Important Notes**
- The CLI supports both JSON and YAML configuration formats
- Use `--verbose` for detailed logging and debugging
- Generator mappings can be provided via command line or file
- All generated configurations are validated before data generation
- The CLI is designed for both interactive use and automation scripts

**Domain Coverage**: GenXData includes 175+ generators across 9 domains:
  - **Person** (31 generators): Names, demographics, contact information
  - **Geographic** (28 generators): Addresses, locations, coordinates
  - **Business** (23 generators): Company data, financial information
  - **Healthcare** (22 generators): Medical conditions, treatments, patient data
  - **Technology** (20 generators): Software versions, hardware specs, network data
  - **IoT Sensors** (20 generators): Device readings, environmental data
  - **Education** (19 generators): Academic subjects, grades, institutions
  - **Transportation** (19 generators): Vehicle data, logistics
  - **Ecommerce** (18 generators): Product data, pricing, orders

### ⚛️ **React Frontend**

**Development Setup:**
```bash
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:5173
```

**Frontend Features:**
- 🎨 **Interactive Configuration Builder**: Visual form-based config creation
- 📊 **Real-time Preview**: See generated data samples before full generation
- 📁 **Multiple Export Formats**: CSV, Excel, JSON, Parquet, and more
- 🎯 **Strategy Selection**: Choose from 13+ generation strategies with parameter forms
- 📋 **Project Management**: Save and load configurations with metadata
- 🔧 **Validation**: Real-time configuration validation and error feedback

#### **🐳 Docker**

**Quick Start:**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:3000
```

**Manual Docker Build:**
```bash
# Build the image
docker build -t genxdata .

# Run the container
docker run -p 8000:8000 genxdata

# Or pull the pre-built image
docker pull genxdata:latest
```

**Production Docker:**
```bash
# Production deployment with environment variables
docker run -d \
  -p 8000:8000 \
  -e WORKERS=4 \
  -e LOG_LEVEL=info \
  --name genxdata-prod \
  genxdata:latest
```

#### **Status**
Docker support is experimental and targets containerizing the CLI; no REST API is exposed.


## 🏗️ Project Structure

```
GenXData/
├── core/                   # Core data generation engine
│   ├── orchestrator.py     # Main processing orchestrator
│   ├── strategies/         # Generation strategies
│   ├── processors/         # Normal and streaming/batch processors
├── cli/                    # Command-line interface
├── utils/                  # Utility functions and helpers
├── configs/                # Configuration files and settings
├── generators/             # 175+ pre-built generators (9 domains)
├── exceptions/             # Custom exception hierarchy
├── messaging/              # Message queue integration (AMQP, Kafka)
├── frontend/               # React web interface
├── dev-docs/               # Architecture and docs
├── examples/               # Example configurations
└── main.py                 # CLI entry point

Key Files:
├── main.py                 # Programmatic/CLI entry point
├── pyproject.toml          # Poetry dependency management
└── docker-compose.yml      # Docker compose (experimental)
```

## ✨ Features

### 🚀 **Comprehensive Data Generation Strategies**
- 🔢 **Numeric Data**: Random numbers, ranges, distributions, series
- 📅 **Date/Time Data**: Date ranges, time series, custom formats
- 📝 **Text Data**: Names, patterns, concatenation, replacements
- 🎲 **Choice Data**: Categorical data with custom probability distributions
- 🔗 **Relationship Data**: Foreign keys, references, dependencies
- 🎭 **Pattern Masking**: Apply masking patterns to sensitive data generation
- 🔢 **Series Generation**: Create sequential or arithmetic series data
- 🔄 **Value Replacement**: Replace or delete specific values based on conditions

### 📁 **Multiple Output Formats**
- 📊 **CSV**: Comma-separated values with custom delimiters
- 📈 **Excel**: Multi-sheet Excel files with formatting
- 🗃️ **JSON**: Structured JSON data with nested objects
- 🚀 **Parquet**: High-performance columnar storage
- ⚡ **Feather**: Fast binary format for data interchange

### ⚙️ **Flexible Configuration**
- 📝 **YAML/JSON Support**: Human-readable configuration files
- 🎯 **Generator Mappings**: 200+ pre-built generators across 9 domains
- 🔧 **Custom Parameters**: Fine-tune generation with strategy-specific parameters
- 📋 **Metadata Support**: Project information, versioning, and documentation

### 🎯 **Advanced Capabilities**
- 🎭 **Pattern Masking**: Apply masking patterns to sensitive data generation
- 🔢 **Series Generation**: Create sequential or arithmetic series data
- 🔄 **Value Replacement**: Replace or delete specific values based on conditions

### 🌐 **Streaming & Queue Integration**
- 📡 **Abstract Queue System**: Support for multiple message queue systems (AMQP, Kafka)
- 🔄 **Real-time Streaming**: Stream data batches to message queues as they're generated
- 🏭 **Enterprise Ready**: Support for Apache Artemis, RabbitMQ, Apache Kafka, and more
- 🔧 **Extensible Architecture**: Easy to add support for new queue systems

### 🖥️ **User-Friendly Interfaces**
- 💻 **Command Line Interface**: Comprehensive CLI with 200+ generators and domain-specific commands
- ⚛️ **React Frontend**: Modern web interface with interactive configuration builder and real-time preview
- 🐳 **Docker**: Experimental containerization for CLI workflows
- 🔧 **Development Tools**: Hot reload, debugging support, and comprehensive error handling

### 📈 **Performance & Monitoring**
- 📊 **Performance Profiling**: Built-in performance monitoring with detailed timing reports
- 💾 **Memory Optimization**: Efficient data generation for large datasets with streaming support
- ⏳ **Progress Tracking**: Real-time progress indicators for long-running generations
- 🏗️ **Scalable Architecture**: Handle datasets from thousands to millions of rows
- ⚡ **Async Processing**: Non-blocking API operations with concurrent request handling

### 🔧 **Developer Experience**
- 🧩 **Extensible Design**: Easy to add custom strategies and generators
- 🛡️ **Type Safety**: Full type hints and validation throughout the codebase
- 📖 **Comprehensive Documentation**: Detailed examples, configuration guides, and API reference
- 🚨 **Error Handling**: Clear error messages and validation feedback
- 🔍 **Debugging Tools**: Verbose logging, performance monitoring, and diagnostic endpoints

## ✅ Current Feature Status

- CLI commands (list-generators, show-generator, by-strategy, create-config, create-domain-configs, generate, stats): working
- Generation modes: standard, streaming, and batch: working via CLI
- File writers: CSV, Excel, JSON, Parquet, Feather, HTML, SQLite: working
- Strategies: 16 strategies available as listed: working
- REST API server and endpoints: not present
- Docker API deployment: not applicable (CLI-focused)

## 🧠 Key Concepts

### 🎯 Strategies (`strategy`)
A strategy defines how the data is going to be generated for a column.

Strategies are the core of the framework. They are the building blocks of the data generation pipeline. Another way to think about it is that strategies are the functions that are used to generate the data. They are the lower-level APIs that are used to generate the data.

### 🏗️ Generators (`generator`)
A generator is a wrapper around a collection of strategies that are used to generate the data for a column.

Generators are the higher-level APIs, an abstraction to hide the parameters of strategies and generate data seamlessly.

For example, Person Name can be a generator that is a wrapper around the [Random Name Strategy](./core/strategies/random_name_strategy.py)

Or a Date of Birth can be a generator that is a wrapper around the [Date Generator Strategy](./core/strategies/date_generator_strategy.py) that is used to generate this kind of data.

**Pre-built Generators**: GenXData now includes domain-specific generator collections in the `generators/` directory:
- 🛒 **ecommerce_generators.json**: Product categories, pricing, order statuses, payment methods
- 🏥 **healthcare_generators.json**: Medical conditions, treatments, patient data
- 🎓 **education_generators.json**: Academic subjects, grades, enrollment data

## 📋 About the tool

GenXData is a comprehensive synthetic data generation framework designed for developers, data scientists, and QA engineers who need realistic test data for their applications. With 16+ generation strategies, 200+ pre-built generators, and support for multiple interfaces (CLI, REST API, Web UI), GenXData provides everything you need to generate high-quality synthetic data at scale.

## 🎲 Available Strategies

1. **RANDOM_NUMBER_RANGE_STRATEGY** - Generate random numbers within specified ranges
2. **DISTRIBUTED_NUMBER_RANGE_STRATEGY** - Generate numbers with custom probability distributions
3. **RANDOM_DATE_RANGE_STRATEGY** - Generate dates within specified ranges and formats
4. **DATE_SERIES_STRATEGY** - Generate sequential date series
5. **DISTRIBUTED_DATE_RANGE_STRATEGY** - Generate dates with weighted distributions
6. **PATTERN_STRATEGY** - Generate data matching regular expression patterns
7. **SERIES_STRATEGY** - Generate sequential or arithmetic series
8. **DISTRIBUTED_CHOICE_STRATEGY** - Generate categorical data with custom probabilities
9. **TIME_RANGE_STRATEGY** - Generate time values within specified ranges
10. **DISTRIBUTED_TIME_RANGE_STRATEGY** - Generate time values with weighted distributions
11. **REPLACEMENT_STRATEGY** - Replace or transform existing values
12. **CONCAT_STRATEGY** - Concatenate multiple columns or values
13. **RANDOM_NAME_STRATEGY** - Generate realistic names with gender and type filtering
14. **DELETE_STRATEGY** - Conditionally delete or nullify values
15. **MAPPING_STRATEGY** - Map values from source to target using dictionaries or files
16. **UUID_STRATEGY** - Generate unique identifiers with customizable formats

Each strategy is highly configurable and can be combined to create complex data generation scenarios.

### 📊 Performance Monitoring

GenXData includes built-in performance monitoring capabilities:

```bash
# Enable performance reporting in CLI
poetry run python -m cli.main_cli generate config.yaml --perf-report

# Or in direct run
python main.py generate config.yaml --perf-report
```

Performance reports include:
- Generation time per strategy
- Memory usage statistics
- Row generation rates
- Bottleneck identification

## 📁 Output Formats

GenXData supports multiple output formats to fit your workflow:

### 💾 Available File Writers

- **CSV_WRITER**: Comma-separated values with custom delimiters
- **EXCEL_WRITER**: Multi-sheet Excel files with formatting options
- **JSON_WRITER**: Structured JSON with nested object support
- **PARQUET_WRITER**: High-performance columnar storage format
- **FEATHER_WRITER**: Fast binary format for data interchange
- **HTML_WRITER**: HTML tables for web display and reporting
- **SQLITE_WRITER**: SQLite database files for direct querying

## 📝 YAML Configuration Support

GenXData fully supports YAML configuration files for better readability and maintainability:

```yaml
metadata:
  name: "User Dataset"
  description: "Sample user data for testing"
  version: "1.0.0"

column_name:
  - name
  - email
  - age

num_of_rows: 1000

configs:
  - column_names: ["name"]
    strategy:
      name: "RANDOM_NAME_STRATEGY"
      params: {}

  - column_names: ["email"]
    strategy:
      name: "PATTERN_STRATEGY"
      params:
        regex: "[a-z]{5}@example.com"

  - column_names: ["age"]
    strategy:
      name: "RANDOM_NUMBER_RANGE_STRATEGY"
      params:
        start: 18
        end: 65
        step: 1
        precision: 0
        unique: false

file_writer:
  type: "CSV_WRITER"
  params:
    output_path: "users.csv"
```

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the Apache-2.0 License - see the LICENSE file for details.

## 🔗 Links

- **Documentation**: [dev-docs/](dev-docs/)
- **Examples**: [examples/](examples/)
- **Architecture**: [dev-docs/architecture-overview.mmd](dev-docs/architecture-overview.mmd)
