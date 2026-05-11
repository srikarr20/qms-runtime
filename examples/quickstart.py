"""
QMS SDK Quickstart Example

Minimal executable example for the
Quantum Measurement Stack (QMS) SDK.
"""

from qos import SDKRuntime


def main():

    print("\n=== QMS SDK Quickstart ===")

    runtime = SDKRuntime()

    result = runtime.run()

    print(result.summary())


if __name__ == "__main__":
    main()
