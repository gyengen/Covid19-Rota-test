import engine.covid19


def cov_calc(par_list, IR, DO, opt1, opt2):
    '''VCDM model calculation.

    Args:
        None

    Returns:
       results (dictinary):

    '''

    # Convert parameteres to int
    N, n, nG = int(par_list[0]), int(par_list[1]), int(par_list[2])

    # Convert parameteres to float
    home_infect = float(par_list[3])

    # Create arrays for the simulation output without optional parameters
    day, total, total_col_plot = [], [], []

    # Create arrays for the simulation output with optional parameters
    total_opt, total_col_plot_opt = [], []

    for i in range(100):

        # Run the simulation
        r = engine.covid19.calc(N, n, 180, nG, home_infect, IR, DO, None, None)

        day.append(r[0])
        total.append(r[1])
        total_col_plot.append(r[2])

        if opt1 is not None:

            # Run the simulation with optionalparameters
            r_opt = engine.covid19.calc(N, n, 180, nG, home_infect,
                                        IR, DO, opt1, opt2)

            total_opt.append(r_opt[1])
            total_col_plot_opt.append(r_opt[2])

    if opt1 is not None:

        # Return simulation output with optional parametes
        return ([day, day],
                [total, total_opt],
                [total_col_plot, total_col_plot_opt])

    else:

        # Return simulation output without optional parametes
        return day, total, total_col_plot
