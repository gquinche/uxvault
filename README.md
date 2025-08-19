<div align="center">
  <picture>
    <source srcset="img/ux-vault-logo-white.svg" media="(prefers-color-scheme: dark)">
    <img src="img/ux-vault-logo.svg" alt="UX Vault" width="500" onerror="this.replaceWith(document.createTextNode('UX Vault'))">
  </picture>
</div>

## Project Overview
UX Vault is an open-source platform designed to streamline the process of conducting card sorting surveys. It allows users to create surveys, share them via links, and analyze results stored locally in their browser through correlation matrices, dendrograms, and more advanced analytics in future updates.

# Streamlit Edition

This is the home of a new Streamlit-powered uxvault platform. This is a complete rewrite of the [original UX Vault](https://github.com/cronozul/p_cards) focused on code quality, maintainability, and extensibility.

## Current Features

- **Card Sorting Creation**
  - Create open or closed card sorting surveys
  - Support for both named and unnamed categories
  - Real-time survey preview
  - Simple and intuitive interface

- **Streamlit-Powered Interface**
  - Real-time updates using Streamlit's reactive framework
  - Clean, consistent design
  - Responsive layout that works across devices

## Roadmap

- **Drag and Drop Interface**
  - Planning to implement intuitive drag-drop card sorting
  - Will maintain fallback interface for accessibility

- **Cloud Integration**
  - Social login support
  - Cloud storage for survey results
  - Share surveys via unique links

- **Analysis Tools**
  - Port existing analysis features from original version:
    - Correlation matrices
    - Dendrograms
  - Add new Python-powered analytics
  - Improved performance for large datasets

## Getting Started

1. Install dependencies:
    ```bash
    poetry install 
    ```
    UV or any other package which reads pyproject should work.
    
2. Run the application:
    ```bash
    streamlit run uxvault/landing.py
    ```

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Legacy Version

The original version with drag-drop and analytics features is available at [cronozul/p_cards](https://github.com/cronozul/p_cards). This new version aims to improve upon its foundation with:
- Cleaner, more maintainable code
- Better Python integration for analysis
- More modular architecture
- Future cloud integration capabilities

## License

This project is licensed under the GPL-3.0 License.

## Acknowledgments

Built with [Streamlit](https://streamlit.io/), the fastest way to build data apps in Python.
