
from functions.get_data import get_asteca_data, get_liter_data, \
    get_bica_database, get_cross_match_data
from functions.get_params import params
import functions.CMD_obs_vs_asteca as cmd
from functions.make_all_plots import make_as_vs_lit_plot, make_kde_plots, \
    make_ra_dec_plots, make_lit_ext_plot, make_int_cols_plot, \
    make_concent_plot, make_radius_plot, make_probs_CI_plot, \
    make_dist_2_cents, make_cross_match, make_cross_match_age_ext, \
    make_DB_ASteCA_CMDs


def d_search(dat_lst, cl_name, name_idx):
    '''
    Search the list of lists obtained when reading the .ods file, for the
    index of the list that contains a given cluster.
    '''
    for i, line in enumerate(dat_lst):
        if cl_name == line[name_idx]:
            return i
    return None


def match_clusters(as_names, cl_dict):
    '''
    Return the index pointing to each cluster in the .ods list, starting
    from the cluster's name taken from the ASteCA list.
    '''

    # Column number for the cluster's name in the .ods file.
    name_idx = cl_dict[0].index(u'Name')

    names_idx = []
    for cl_name in as_names:
        cl_i = d_search(cl_dict, cl_name, name_idx)
        if cl_i is None:
            print 'WARNING: {} not found in ods file.'.format(cl_name)
        else:
            names_idx.append(cl_i)

    return names_idx


def get_DBs_ASteCA_CMD_data():
    '''
    '''
    # db = 'G10'
    # mc_cls = [['B112', 'SL218', 'KMHK979', 'KMHK229', 'HW22', 'HW42', 'HW63',
    #           'KMHK378', 'SL446A', 'L91'],
    #           ['SL674', 'SL290', 'HW40', 'HW31', 'BSDL268', 'HW41', 'SL162',
    #           'SL230', 'SL555', 'SL132'],
    #           ['HS264', 'BRHT4B', 'SL96', 'L63', 'HS38', 'NGC1839', 'NGC294',
    #           'B34', 'NGC1793', 'L72'],
    #           ['NGC2093', 'KMHK112', 'BS265', 'SL678', 'SL35', 'B39', 'L50',
    #           'L30', 'SL397', 'NGC1863'],
    #           ['BRHT45A', 'HW55', 'NGC1838', 'KMHK1055', 'SL444', 'L62',
    #           'SL505', 'L34', 'H88-320', 'HS412'],
    #           ['LW54', 'L58', 'L49', 'SL510', 'SL551', 'BSDL631', 'L45',
    #           'H88-316', 'BS35', 'L35'],
    #           ['SL579']]

    db = 'C06'
    mc_cls = [['B47', 'H86-70', 'L63', 'L62', 'B39', 'BS121', 'BS88',
               'NGC294', 'L19', 'L34'],
              ['L30', 'B34', 'L72', 'NGC419', 'BS35', 'L35']]

    db_cls = [[] for _ in mc_cls]
    for i, cl_lst in enumerate(mc_cls):
        for cl in cl_lst:

            # Obtain CMD limits for cluster.
            x_max_cmd, x_min_cmd, y_min_cmd, y_max_cmd = cmd.diag_limits(cl)

            # Obtain age and extinction from 'matched_clusters.dat' file.
            db_a, db_e, gal = cmd.get_DB_age_ext(cl, db)
            if gal == 'SMC':
                if db == 'G10':
                    db_z, db_d = 0.004, 18.9
                elif db == 'C06':
                    db_z, db_d = 0.008, 18.9
            elif gal == 'LMC' and db == 'G10':
                db_z, db_d = 0.008, 18.5

            # Fetch which run holds this cluster's membership data.
            run = cmd.get_cl_run(cl)
            # Fetch what 'input_XX' folder in the above run contains the
            # membership file.
            inpt = cmd.get_input_folder(cl, run)
            # Path where the members file is stored.
            cl_path = '/media/rest/github/mc-catalog/runs/' + run + \
                '_run/output/' + inpt + '/' + cl + '_memb.dat'
            # Membership data for cluster.
            cl_reg_fit, cl_reg_no_fit = cmd.get_memb_data(cl_path)

            # Obtain DB isochrone.
            lit_isoch = cmd.get_isoch('DB', db_z, db_a, db_e, db_d)

            # Obtain ASteCA parameters.
            as_z, as_z_str, as_a, as_e, as_d = cmd.get_asteca_params(cl)
            # Obtain ASteCA isochrone.
            asteca_isoch = cmd.get_isoch('AS', as_z_str, as_a, as_e, as_d)

            db_cls[i].append([x_min_cmd, x_max_cmd, y_min_cmd, y_max_cmd, cl,
                              db, gal, cl_reg_fit, cl_reg_no_fit, lit_isoch,
                              asteca_isoch, db_z, db_a, db_e, db_d, as_z, as_a,
                              as_e, as_d])
            print '{} {} data obtained'.format(db, cl)

    return db, db_cls


def check_diffs(in_params):
    '''
    check differences between ASteCA values and literature values for given
    parameters.
    '''
    gal_names, zarr, aarr, earr, darr, rarr, marr, dist_cent, ra, dec = \
        [in_params[_] for _ in ['gal_names', 'zarr', 'aarr', 'earr', 'darr',
                                'rarr', 'marr', 'dist_cent', 'ra', 'dec']]

    gal = ['SMC', 'LMC']

    # For SMC and LMC.
    for j in [0, 1]:

        # For each cluster.
        cl_count = 0
        for i, name in enumerate(gal_names[j]):
            flag_cl = False

            # For each parameter.
            for k, par in enumerate([aarr]):
                diff = par[j][0][i] - par[j][1][i]
                if par[j][1][i] > -99.:

                    # # Age diffs.
                    # print '{} {}, {:.2f} vs {:.2f} , {:.2f}'.format(
                    #     gal[j], name, par[j][0][i], par[j][1][i], diff)

                    # Age.
                    if abs(diff) > 0.5:
                        flag_cl = True
                        # AsteCA vs Literature Log(age) difference.
                        rel_diff = par[j][0][i] - par[j][1][i]
                        print '{} {}, {:.2f} vs {:.2f} , {:.2f}'.format(
                            gal[j], name, par[j][0][i], par[j][1][i], rel_diff)

            #         # Extinction.
            #         if k == 2 and diff > pars_diff[2]:
            #             flag_cl = True
            #             print '{} {} {}, {:.2f} vs {:.2f}'.format(gal[j],
            #                 name, p_n[k], par[j][0][i], par[j][1][i])

            #         # Distance.
            #         if k == 3 and diff > pars_diff[3]:
            #             flag_cl = True
            #             print '{} {} {}, {:.2f} vs {:.2f}'.format(gal[j],
            #                 name, p_n[k], par[j][0][i], par[j][1][i])

            #         # Radius.
            #         if k == 4 and diff > pars_diff[4]:
            #             flag_cl = True
            #             print '{} {} {}, {} vs {}'.format(gal[j], name,
            #                 p_n[k], par[j][0][i], par[j][1][i])

            # # Mass.
            # if marr[j][0][i] > 0.:
            #     flag_cl = True
            #     print '{} {} {}'.format(gal[j], name, marr[j][0][i])

            # # Distance to center.
            # print '{} {} {:.2f} {} {} {}'.format(
            #     gal[j], name, dist_cent[j][i] / 1000., darr[j][0][i],
            #      ra[j][i], dec[j][i])

            if flag_cl:
                cl_count += 1

        print '\n* {}, Clusters with \delta log(age)>0.5: {}\n'.format(
            gal[j], cl_count)


def make_plots(in_params, bica_coords, cross_match):
    '''
    Make each plot sequentially.
    '''

    for j, gal in enumerate(['SMC', 'LMC']):
        make_as_vs_lit_plot(gal, j, in_params)
        print '{} ASteCA vs literature plots done.'.format(gal)

    #     make_kde_plots(gal, j, in_params)
    #     print '{} KDE maps done.'.format(gal)

    # make_ra_dec_plots(in_params, bica_coords)
    # print 'RA vs DEC plots done.'

    # make_lit_ext_plot(in_params)
    # print 'ASteca vs MCEV vs SandF extinction plot done.'

    # make_int_cols_plot(in_params)
    # print 'Integrated colors plot done.'

    # make_concent_plot(in_params)
    # print 'Concentration parameter plot done.'

    # make_radius_plot(in_params)
    # print 'ASteCA radius (pc) vs parameters plot done.'

    # make_probs_CI_plot(in_params)
    # print 'ASteCA probabilities versus CI done.'

    # make_dist_2_cents(in_params)
    # print 'Distances to center of MC done.'

    # make_cross_match(cross_match)
    # print 'Cross-matched clusters done.'

    # make_cross_match_age_ext(cross_match, in_params)
    # print 'Age and extinction diffs for cross-matched clusters done.'


def main():
    '''
    Call each function.
    '''
    # Read Bica et al. (2008) database.
    bica_coords = get_bica_database()

    # Read data from ASteca output file.
    as_names, as_pars = get_asteca_data()
    print 'ASteCA data read from output file.'

    # Read literature data.
    cl_dict = get_liter_data()
    print 'Literature data read from .ods file.'

    # Read cross-matched clusters.
    cross_match = get_cross_match_data()
    print 'Cross-matched data read.'

    # Match clusters.
    names_idx = match_clusters(as_names, cl_dict)
    print 'Cluster parameters matched.'

    # Get data parameters arrays.
    in_params = params(as_names, as_pars, cl_dict, names_idx)
    print 'Dictionary of parameters obtained.\n'

    # Check for differences in ASteCA vs Lit values.
    check_diffs(in_params)

    # Make final plots.
    make_plots(in_params, bica_coords, cross_match)

    # # Put this plot here since it does not depend on any parameter obtained
    # # here.
    # db, db_cls = get_DBs_ASteCA_CMD_data()
    # make_DB_ASteCA_CMDs(db, db_cls)
    # print 'CMDs for matched DB and ASteCA clusters done.'

    print '\nEnd.'


if __name__ == "__main__":
    main()
