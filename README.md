# Code Plagiarism Analysis

## 1. Collaboration rules

### 1.1. Code style

- C++ google style ([guide](https://google.github.io/styleguide/cppguide.html))

- Python PEP8 style ([guide](https://www.python.org/dev/peps/pep-0008/))

### 1.2. Taskboard

- Trello [invite](https://trello.com/invite/b/sovrr5dJ/afd614ed4dc319c14986e1792b53d896/identifying-plagiarism-in-source-code)

## 2. Install requirements

- pip install -r ./requirements.txt

- python version 3.6+ or even 3.8+

## 3. Tests

- Testing for C/C++ analyzer
  > Test of canalyze.py functions
  ```
    $ python3 -m unittest test_canalyze.py
  ```

  > Flag `-v` for more testing information
  ```
    $ python3 -m unittest -v test_canalyze.py
  ```
- Testing for python analyzer
  > Test of pyanalyze.py functions
  ```
    $ python3 -m unittest test_pyanalyze.py
  ```

  > Flag `-v` for more testing information
  ```
    $ python3 -m unittest -v test_pyanalyze.py
  ```