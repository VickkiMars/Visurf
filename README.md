# Visurf

**Visurf** is an AI-powered surfer that uses the Playwright engine to browse the web. It is available in two versions: 

- **v1**: A synchronous version of the surfer, utilizing regular programming techniques.
- **v2**: An asynchronous version of the surfer, using async programming with Python.

## Versions

### v1: Regular Programming
- **Run**: 
  ```bash
  python cli.py
  ```

### v2: Async Programming
- **Run**:
  ```bash
  python surfer.py
  ```
  
v2 introduces improved performance by allowing non-blocking asynchronous operations, while v1 is more traditional with blocking synchronous calls.

### Installation
**Prerequisites**
Ensure you have Python 3.6 or higher installed.

Make sure pip is updated:
```bash
  pip install --upgrade pip
```

**Setup**
Clone the repository:

```bash
  git clone https://github.com/VickkiMars/Visurf.git
  cd Visurf
```
**Install required dependencies**:
```bash
  pip install -r requirements.txt
```

### Usage
**v1 (Synchronous)**
Run the following command to start the surfer:

```bash
  python cli.py
```

Follow the prompts in the CLI to browse the web with the Playwright engine.

v2 (Asynchronous)
Start the asynchronous version:

bash
Copy
Edit
python surfer.py
Enjoy the non-blocking, efficient browsing experience with async programming.

Features
Web scraping and data extraction using Playwright.

AI-powered browsing using machine learning models.

Available in both synchronous and asynchronous modes for flexibility.

Contributing
We welcome contributions! Please fork the repository, make changes, and create a pull request.

Steps to Contribute:
Fork the repository.

Create a new branch (git checkout -b feature-branch).

Make your changes.

Commit your changes (git commit -m 'Add new feature').

Push to your forked repository (git push origin feature-branch).

Create a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
