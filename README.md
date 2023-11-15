# finpricing

`finpricing` is a Python package designed for advanced financial pricing and risk management. It features pricing models and design patterns that align with industry standards and market conventions. However, it's important to note a few aspects:

1. The industry typically develops pricing libraries in C++ or C# to optimize performance. Speed, however, is not the primary objective of this package. The focus is on presenting rigorous and often overlooked pricing models in a modern, readable language, while ensuring precision.
2. The author's expertise is predominantly in Fixed Income products and derivatives (as of 2023). Contributions to expand the scope of this package are highly encouraged.

The implementation follows the instrument + market + model paradigm. The major modules now (as of 2023/11) are,

- `finpricing.instruments`:
  - Fixed Coupon Bond
  - Credit Default Swap

- `finpricing.markets`:
  - Discount Curve: flat forward assumption, which is the most common curve construction method
  - Survival Curve: piecewise constant hazard rate and Nelson-Siegel-Svensson (NSS) curve
  - CDS Curve (in progress)

- `finpricing.models`:
  - Fixed Bond pricer: risky pricing of fixed coupon bond considering survival curve and recovery rate
  - Bond Basis Solver: solve for the bond basis on top of the discount curve or the survival curve
  - Bond Curve Solver: calibration of the NSS survival curve for a portfolio of bonds of the same issuer by minimizing the bond basis
  - CDS pricer: risky pricing of CDS contracts
  - CDS Par Spreads

- `finpricing.utils` examples:
  - Date: internal date representation
  - Day Count: day count convention, e.g. Actual/360, Actual/365, etc.
  - Calendar: holiday calendar for adjustment of business days
  - Date Generator: generate dates for instrument cash flows

## Installation

```bash
$ pip install finpricing
```

## Usage

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`finpricing` was created by Yiming Zhang. It is licensed under the terms of the MIT license.

## Credits

`finpricing` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
