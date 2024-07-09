from src.Server import Server
from argparse import ArgumentParser


def main():
    # Initialize the argument parser
    parser = ArgumentParser(description="Run the SugarScape with Spice simulation.")

    # Add all the arguments
    parser.add_argument("--width", type=int, default=50, help="The width of the grid.")
    parser.add_argument("--height", type=int, default=50, help="The height of the grid.")
    parser.add_argument("--initial_population", type=int, default=300, help="The number of traders to start with.")
    parser.add_argument("--metabolism_mean", type=float, default=5, help="The mean metabolism for traders.")
    parser.add_argument("--vision_mean", type=float, default=3, help="The mean vision for traders.")
    parser.add_argument("--max_age_mean", type=float, default=85, help="The mean maximum age for traders.")
    parser.add_argument("--tax_scheme", type=str, default="progressive", help="The tax scheme to use.")
    parser.add_argument("--tax_steps", type=int, default=20, help="The number of tax steps to use.")
    parser.add_argument("--tax_rate", type=float, default=0.1, help="The tax rate to apply to all trades.")
    parser.add_argument("--distributer_scheme", type=str, default="progressive", help="The distributer scheme to use.")
    parser.add_argument("--distributer_steps", type=int, default=20, help="The number of distributer steps to use.")
    parser.add_argument("--repopulate_factor", type=float, default=10,
                        help="The factor used to determine when to repopulate traders.")
    parser.add_argument("--map_scheme", type=str, default="uniform", help="The scheme to use for generating the map.")
    parser.add_argument("--cell_regeneration", type=float, default=1,
                        help="The amount of sugar to regenerate in each cell.")

    # Parse the arguments
    args = parser.parse_args()

    # Create the server
    server = Server(
        width=args.width,
        height=args.height,
        initial_population=args.initial_population,
        metabolism_mean=args.metabolism_mean,
        vision_mean=args.vision_mean,
        max_age_mean=args.max_age_mean,
        tax_scheme=args.tax_scheme,
        tax_steps=args.tax_steps,
        tax_rate=args.tax_rate,
        distributer_scheme=args.distributer_scheme,
        distributer_steps=args.distributer_steps,
        repopulate_factor=args.repopulate_factor,
        map_scheme=args.map_scheme,
        cell_regeneration=args.cell_regeneration
    )

    # Run the server
    server.launch()


if __name__ == "__main__":
    main()
