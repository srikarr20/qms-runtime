import argparse

from qos.runtime import (

    RuntimeExecution,

    RuntimeSnapshot,

    ReplayRuntime,

    RuntimeValidator,

    RuntimeBenchmark,

    RuntimeAnalytics,

)


# ==========================================================
# RUNTIME
# ==========================================================

def run_runtime(args):

    runtime = RuntimeExecution(

        runtime_steps=args.steps

    )

    field_history, tensor = (
        runtime.execute()
    )

    snapshot = RuntimeSnapshot.save(

        field_history,

        tensor,

    )

    print(
        "\n=== Runtime Complete ==="
    )

    print(snapshot)


# ==========================================================
# REPLAY
# ==========================================================

def replay_runtime(args):

    replay = ReplayRuntime(
        args.snapshot
    )

    replay.replay()


# ==========================================================
# VALIDATE
# ==========================================================

def validate_runtime(args):

    snapshot = RuntimeSnapshot.load(
        args.snapshot
    )

    validator = RuntimeValidator(

        snapshot["runtime_tensor"]

    )

    validation = (
        validator.validate()
    )

    print(
        "\n=== Validation ==="
    )

    print(validation)

    validator.export(
        validation
    )


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark_runtime(args):

    benchmark = RuntimeBenchmark(
        args.profile
    )

    result = benchmark.run()

    print(
        "\n=== Benchmark Result ==="
    )

    print(result)


# ==========================================================
# ANALYTICS
# ==========================================================

def analytics_runtime(args):

    analytics = RuntimeAnalytics(

        args.profiles

    )

    analytics.run()

    analytics.export()


# ==========================================================
# SNAPSHOT INFO
# ==========================================================

def snapshot_info(args):

    snapshot = RuntimeSnapshot.load(
        args.snapshot
    )

    print(
        "\n=== Snapshot Metadata ==="
    )

    print(
        snapshot["metadata"]
    )


# ==========================================================
# PROFILES
# ==========================================================

def list_profiles(args):

    profiles = [

        "ideal_runtime",

        "medium_runtime",

        "noisy_runtime",

        "collapse_runtime",

        "adaptive_runtime",

    ]

    print(
        "\n=== Runtime Profiles ==="
    )

    for p in profiles:

        print(p)


# ==========================================================
# MAIN
# ==========================================================

def main():

    parser = argparse.ArgumentParser(

        prog="qms",

        description=
        "QOS Runtime Core CLI",

    )

    subparsers = parser.add_subparsers()

    # ======================================================
    # runtime
    # ======================================================

    runtime_parser = subparsers.add_parser(
        "runtime"
    )

    runtime_parser.add_argument(

        "--steps",

        type=int,

        default=240,

    )

    runtime_parser.set_defaults(
        func=run_runtime
    )

    # ======================================================
    # replay
    # ======================================================

    replay_parser = subparsers.add_parser(
        "replay"
    )

    replay_parser.add_argument(
        "snapshot"
    )

    replay_parser.set_defaults(
        func=replay_runtime
    )

    # ======================================================
    # validate
    # ======================================================

    validate_parser = subparsers.add_parser(
        "validate"
    )

    validate_parser.add_argument(
        "snapshot"
    )

    validate_parser.set_defaults(
        func=validate_runtime
    )

    # ======================================================
    # benchmark
    # ======================================================

    benchmark_parser = subparsers.add_parser(
        "benchmark"
    )

    benchmark_parser.add_argument(
        "profile"
    )

    benchmark_parser.set_defaults(
        func=benchmark_runtime
    )

    # ======================================================
    # analytics
    # ======================================================

    analytics_parser = subparsers.add_parser(
        "analytics"
    )

    analytics_parser.add_argument(

        "profiles",

        nargs="+",

    )

    analytics_parser.set_defaults(
        func=analytics_runtime
    )

    # ======================================================
    # snapshot
    # ======================================================

    snapshot_parser = subparsers.add_parser(
        "snapshot"
    )

    snapshot_parser.add_argument(
        "snapshot"
    )

    snapshot_parser.set_defaults(
        func=snapshot_info
    )

    # ======================================================
    # profiles
    # ======================================================

    profiles_parser = subparsers.add_parser(
        "profiles"
    )

    profiles_parser.set_defaults(
        func=list_profiles
    )

    # ======================================================
    # RUN
    # ======================================================

    args = parser.parse_args()

    if hasattr(args, "func"):

        args.func(args)

    else:

        parser.print_help()


if __name__ == "__main__":

    main()
