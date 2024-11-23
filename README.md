# Swarm Dev Team

## About

Sample [Open AI Swarm](https://github.com/openai/swarm/) development team implementation with a log that shows communication between agents. [Sample output](output.txt).

Manager + Developer + Tester + Reporter

Team is reponsible to write and test python function based on instructions and function template.

## Setup

- Copy .env.sample to .env and fill in your Open AI key information
```
cp .env.sample .env
vi .env
```

- Install poetry packages
```
poetry install
```

## Run
```
poetry shell
python run.py
```

See `context_variables` for inputs

## Ollama

To run with local [Ollama](https://ollama.com/) model **llama3.2** and **qwen2.5-coder** flip the `ollama` flag at the top of the run.py class