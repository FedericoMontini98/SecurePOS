import sys

from segregation_system.segregation_system_controller import SegregationSystemController


def main():
    controller = SegregationSystemController()
    controller.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
