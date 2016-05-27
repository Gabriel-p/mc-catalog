
import numpy as np
from kde_map import kde_2d
from astroML.plotting import hist as h_ML
from scipy.integrate import simps


def age_met_rel(xarr, xsigma, yarr, ysigma, grid_step):
    '''
    Generate a grid in the age-metallicity diagram.
    1- Obtain the 2D KDE of the age-metallicity parameters space.
    2- Obtain a unique [Fe/H] value for each age value in the grid, *weighted*
    by the KDE map.
    3- Obtain the error associated to that [Fe/H] value.

    See: http://math.stackexchange.com/q/1457390/37846
    '''

    # Define 2D space extension where the KDE will be obtained.
    x_min, x_max = min(np.array(xarr) - np.array(xsigma)), \
        max(np.array(xarr) + np.array(xsigma))
    # These range defines the metallicity values (met_vals) that will be
    # weighted by the KDE below.
    y_min, y_max = min(np.array(yarr) - np.array(ysigma)), \
        max(np.array(yarr) + np.array(ysigma))

    # Grid density defined using the 'grid_step'.
    gd = int((y_max - y_min) / grid_step)

    # Generate metallicity values as in grid. Invert list so the weighted
    # average is obtained correctly.
    met_vals = np.linspace(y_min, y_max, gd)[::-1]
    age_vals = np.linspace(x_min, x_max, gd)

    # Obtain age-metallicity 2D KDE for the entire defined range.
    ext = [x_min, x_max, y_min, y_max]
    z = kde_2d(np.array(xarr), np.array(xsigma), np.array(yarr),
               np.array(ysigma), ext, gd)
    # Order KDE in age columns where each column is associated with an age.
    a_m_kde = zip(*z)

    # Obtain metallicity weighted average for each age value.
    met_weighted = [[], []]
    for age_col in a_m_kde:
        # # Filter out points with very small values (assign 0. value)
        # min_w = max(age_col) / 20.
        # age_col2 = []
        # N = 0
        # for _ in age_col:
        #     if _ < min_w:
        #         age_col2.append(0.)
        #         N += 1
        #     else:
        #         age_col2.append(_)
        # age_col = np.array(age_col2)

        # Metallicity values given by the KDE for the entire metallicity range,
        # for a single age value.
        age_col = np.array(age_col)

        # Obtain weighted metallicity for this *single* age value.
        sum_age_col = sum(age_col)
        met_w = sum(met_vals * age_col) / sum_age_col
        met_weighted[0].append(met_w)

        # Obtain standard deviation.
        nume = sum(age_col * (met_w - met_vals) ** 2)
        deno = sum_age_col - (sum(age_col ** 2) / sum_age_col)
        stdev_met_w = np.sqrt(nume / deno)
        met_weighted[1].append(stdev_met_w)

    return age_vals, met_weighted


def get_amr_asteca(in_params):
    """
    Obtain AMR for both MCs. Steps:

    0- Filter OCs if necessary, for testing.
    1- Add old LMC OCs if necessary, for testing.
    2- Convert log(ages) to Age (Gyr) (same for errors)
    3- Define values for grid_step and binning. The latter is the one that will
       affect the AMR the most. The former just needs to be small enough to
       allowing sampling a fine grid in the age-metallicity space.
    4- Obtain equispaced age values in grid, and equispaced *weighted* [Fe/H]
       values in grid (age_vals, met_weighted).
    5- Obtain bin edges for the entire age range.
    6- For each age range, obtain the average integral of the weighted [Fe/H],
       using Simpson's rule. The associated age value is the mid point of the
       age range.
    7- Use Monte Carlo to calculate errors for the representative [Fe/H] value
       for that age range.
    """

    zarr, zsigma, aarr, asigma = [
        in_params[_] for _ in ['zarr', 'zsigma', 'aarr', 'asigma']]

    # First index k indicates the galaxy (0 for SMC, 1 for LMC), the second
    # index 0 indicates ASteCA values.
    # k=0 -> SMC, k=1 ->LMC
    age_gyr, age_vals, met_weighted, feh_f, age_rang_MCs =\
        [[], []], [[], []], [[], []], [[], []], [[], []]
    for k in [0, 1]:
        # Exclude OCs with extremely low metallicities.
        age_f, age_err_f, feh_err_f = [], [], []
        for v in zip(*[aarr[k][0], asigma[k][0], zarr[k][0], zsigma[k][0]]):
            # To filter out HW85 and NGC294
            # if v[2] > -1.5:
            # To filter out the 4 LMC OCs with large ages ans metallicities.
            # if not (9.48 < v[0] < 9.6 and v[2] > -0.3):
            # To include all OCs.
            if True:
                age_f.append(v[0])
                age_err_f.append(v[1])
                feh_f[k].append(v[2])
                feh_err_f.append(v[3])
            else:
                print v

        # #####################################################################
        # # Add old LMC OCs taken from Piatti & Geisler (2013)
        # old_lmc_OCs = [[9.93, 10.09, 10.13, 10.11, 10.13, 10.09, 10.13,
        #                 10.15, 10.17, 10.09, 10.09, 10.09],
        #                [-1.049, -1.202, -1.369, -1.418, -1.62, -1.746,
        #                 -1.847, -1.865, -2.049, -1.997, -2.095, -2.196]]
        # if k == 1:
        #     age_f = age_f + old_lmc_OCs[0]
        #     feh_f[k] = feh_f[k] + old_lmc_OCs[1]
        #     # Add a reasonable but small error.
        #     age_err_f = age_err_f + [0.05]*len(old_lmc_OCs[0])
        #     feh_err_f = feh_err_f + [0.05]*len(old_lmc_OCs[0])
        # #####################################################################

        # Age in Gyrs.
        age_gyr[k] = [10 ** (np.asarray(age_f) - 9),
                      np.asarray(age_err_f) * np.asarray(age_f) *
                      np.log(10) / 5.]

        # THESE NUMBERS AFFECT THE SHAPE OF THE FINAL AMR.
        # Grid step.
        grid_step = 0.01
        # Define method or number of bins for the age range.
        bn = 'knuth'

        # Weighted metallicity values for an array of ages.
        # Max limit on very large met errors.
        zsig = [min(2., _) for _ in feh_err_f]
        age_vals[k], met_weighted[k] = age_met_rel(
            age_gyr[k][0], age_gyr[k][1], feh_f[k], zsig, grid_step)

        # import matplotlib.pyplot as plt
        # f, (ax1, ax2) = plt.subplots(1, 2)
        # ax1.scatter(age_vals[k], met_weighted[k][0])

        # Obtain bin edges for the entire age range.
        astroML_edges = h_ML(age_gyr[k][0], bins=bn, color='black',  # ax=ax2,
                             histtype='step', normed=True)
        age_temp, met_temp, met_err_temp = [], [], []
        # Add to list the min and max value of age where the KDE was obtained.
        age_rang = [min(age_vals[k])] + list(astroML_edges[1]) +\
            [max(age_vals[k])]

        # Print info to screen.
        gal = ['SMC', 'LMC']
        delta = np.mean([abs(j-i) for i, j in zip(age_rang, age_rang[1:])])
        print('{}:  {} bins; {:.2f} average bin width; {:.2f}-{:.2f}'
              ' limits'.format(gal[k], len(age_rang), delta, min(age_rang),
                               max(age_rang)))

        # Obtain average integral in each age range. This is the [Fe/H] value
        # for that range.
        for i, edge in enumerate(age_rang):
            # Separate values for each interval in the age range, defined by
            # the edges obtained above.
            if i != (len(age_rang) - 1):
                min_a = edge
                max_a = age_rang[i+1]
            else:
                min_a = edge
                max_a = max(age_vals[k])
            met_in_bin = [[], [], []]
            for a, m, e_m in zip(*[age_vals[k], met_weighted[k][0],
                                 met_weighted[k][1]]):
                if min_a <= a < max_a:
                    met_in_bin[0].append(a)
                    met_in_bin[1].append(m)
                    met_in_bin[2].append(e_m)
            # Integrate the age interval, using Simpson's rule. Leave out
            # points were the integration fails.
            try:
                # Compute the area using the composite Simpson's rule.
                fe_h_int = simps(met_in_bin[1], met_in_bin[0])
                # Integration limits.
                a_0, a_1 = min(met_in_bin[0]), max(met_in_bin[0])
                # The x axis value (age) is the average age for the interval.
                # The y axis value ([Fe/H]) is the average of the integral.
                age_avrg, fe_h_avrg= (a_0+a_1)/2., fe_h_int/(a_1-a_0)
                # Store unique AMR x,y values.
                age_temp.append(age_avrg)
                met_temp.append(fe_h_avrg)
                # Obtain associated error for this average [Fe/H]_age value,
                # using Monte Carlo.
                mc_met = []
                for _ in range(500):
                    # Draw [Fe/H] random values from Gaussian distribution.
                    feh_ran = np.random.normal(met_in_bin[1], met_in_bin[2])
                    # Store integral.
                    mc_met.append(simps(feh_ran, met_in_bin[0])/(a_1-a_0))
                # The standard deviation of the above MC integrals, is the
                # associated error of the [Fe/H] value for this age range.
                met_err_temp.append(np.std(mc_met))
            except:
                pass
        # plt.show()
        # Store AMR function values.
        age_vals[k], met_weighted[k] = age_temp, [met_temp, met_err_temp]
        age_rang_MCs[k] = age_rang

    amr_asteca = [age_vals, met_weighted, age_gyr, feh_f, age_rang_MCs]
    return amr_asteca
