# Contributing to Chase the Cloud

Thank you for your interest in contributing! We welcome contributions from everyone.

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive environment.

## How to Contribute

### Reporting Bugs
- Check if the bug has already been reported in Issues
- Include Python version, OS, and CUDA version (if applicable)
- Provide a minimal reproducible example
- Include error traceback and logs

### Suggesting Enhancements
- Clearly describe the enhancement and its benefits
- Provide examples of how it would be used
- Link to relevant research papers or references if applicable

### Submitting Code Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/insat-cloud-forecasting.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Make your changes**
   - Keep commits atomic and well-documented
   - Follow the coding style (see below)
   - Add tests for new functionality
   - Update documentation as needed

5. **Code Style**
   - Use **Black** for code formatting:
     ```bash
     black .
     ```
   - Use **isort** for import organization:
     ```bash
     isort .
     ```
   - Use **Flake8** for linting:
     ```bash
     flake8 .
     ```
   - Follow PEP 8 guidelines
   - Add docstrings to functions and classes

6. **Testing**
   - Write tests for new functionality
   - Ensure all existing tests pass:
     ```bash
     pytest
     ```

7. **Commit Message Format**
   ```
   [TYPE] Short description (50 chars max)
   
   Longer description explaining the changes and why they were made.
   
   Fixes #issue_number (if applicable)
   ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
   
   Example:
   ```
   feat: Add temperature-based cloud classification
   
   - Implement temperature thresholding in DDPMScheduler
   - Add metrics for TIR1-based classification accuracy
   
   Fixes #42
   ```

8. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Fill out the PR template completely
   - Link any related issues
   - Request reviewers if applicable

## Pull Request Guidelines

- Keep PRs focused on a single feature/fix
- Include a clear description of changes
- Update README.md if adding new functionality
- Add tests for any new code
- Ensure CI/CD checks pass

## Development Workflow

### Setting up IDE for Development

**VS Code**:
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

### Running Tests
```bash
pytest -v                    # Verbose output
pytest --cov=.              # With coverage
pytest -k test_name         # Specific test
```

## Documentation

- Update docstrings for modified functions
- Keep README.md current
- Add comments for complex logic
- Use type hints in function signatures

Example docstring:
```python
def process_satellite_image(img_path: str, channels: List[str]) -> np.ndarray:
    """
    Process INSAT3DR satellite image from H5 file.
    
    Args:
        img_path (str): Path to .h5 satellite file
        channels (List[str]): List of channels to extract ['IMG_TIR1', 'IMG_TIR2', 'IMG_WV']
    
    Returns:
        np.ndarray: Processed image array of shape (3, 64, 64)
    
    Raises:
        FileNotFoundError: If image file doesn't exist
        KeyError: If specified channels are not in the file
    """
```

## Areas Where Help is Needed

- [ ] Optimization and performance improvements
- [ ] GPU memory optimization for larger batch sizes
- [ ] Model architecture experiments (UNet variants, attention mechanisms)
- [ ] Data augmentation techniques
- [ ] Cloud detection algorithms comparison
- [ ] Real-time inference optimization
- [ ] Docker containerization
- [ ] CI/CD pipeline improvements
- [ ] Documentation and tutorials
- [ ] Bug fixes and issue resolution

## Project Leads

- Primary: [@yourusername](https://github.com/yourusername)
- Co-maintainers: (add as needed)

## Questions?

- Check existing issues and discussions
- Open a new discussion for questions
- Contact maintainers directly

---

Thank you for contributing to making cloud forecasting more accurate! 🌩️
