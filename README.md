# Tando: AI-Assisted Study Platform 

**Tando** is an AI-assisted studying platform written with FastAPI and designed to enhance learning efficiency. It offers a suite of AI powered tools aimed at helping users study more effectively and maximize the benefits from their study materials.

## Features

- **AI-Powered Study Tools**: Leverages artificial intelligence to provide intelligent study aids.
- **Efficient Learning Strategies**: Implements methods to optimize study sessions and material retention.
- **User-Friendly Interface**: Designed with a focus on ease of use to facilitate seamless studying experiences.

## Project Structure

```
Tando/
├── alembic/             # Database migration scripts
├── app/                 # Core application code
├── docker/              # Docker configuration files
├── tests/               # Test suites for the application
├── .gitignore           # Specifies files to ignore in version control
├── alembic.ini          # Alembic configuration file
├── project_structure    # Documentation of project structure
├── requirements.txt     # List of project dependencies
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Muyiiwaa/Tando.git
   cd Tando
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**
   ```bash
   # Assuming the entry point is defined in app/main.py
   python app/main.py
   ```

2. **Access the application**
   Navigate to the appropriate URL (e.g., `http://localhost:8000`) in your browser to interact with Tando.

