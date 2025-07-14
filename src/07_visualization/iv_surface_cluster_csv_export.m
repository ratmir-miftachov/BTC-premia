% This file is to get average IV surface in HV and LV clusters, and stored in
% csv files

clc; clear; close all;

% ---------- Step 0: Load clustering dates ----------
common_dates_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/common_dates_cluster.csv";
T_cluster = readtable(common_dates_path);

dates_Q = containers.Map('KeyType', 'double', 'ValueType', 'any');
dates_Q(0) = datetime(T_cluster.Date(T_cluster.Cluster == 0)); % HV
dates_Q(1) = datetime(T_cluster.Date(T_cluster.Cluster == 1)); % LV
dates_Q(2) = sort([dates_Q(0); dates_Q(1)]);                   % overall

% ---------- Grid Setup ----------
all_tau = 3:60;
all_moneyness = -1:0.01:1;

% ---------- Input Data ----------
iv_path = 'IV/IV_surface_SVI/Tau-independent/unique/moneyness_step_0d01/';
file_list = dir(fullfile(iv_path, 'interpolated_*_allR2.csv'));

% ---------- Loop over cluster IDs ----------
for cid = [0, 1, 2]  % 0=HV, 1=LV, 2=overall
    % Prepare accumulators
    iv_sum_surface = zeros(length(all_tau), length(all_moneyness));
    iv_count_surface = zeros(length(all_tau), length(all_moneyness));
    
    for k = 1:length(file_list)
        filename = fullfile(iv_path, file_list(k).name);
        T = readtable(filename);

        current_date = datetime(T{2,1});
        if ~ismember(current_date, dates_Q(cid))
            continue;
        end

        mny_vals = T{1,3:end};
        iv_surface = nan(length(all_tau), length(all_moneyness));

        for i = 2:height(T)
            tau = T{i,2};
            if ~ismember(tau, all_tau)
                continue;
            end

            iv_row = T{i, 3:end};

            for j = 1:length(mny_vals)
                m = mny_vals(j);
                iv = iv_row(j);

                if isnan(iv) || m < -1 || m > 1
                    continue;
                end

                tau_idx = find(all_tau == tau);
                [~, mny_idx] = min(abs(all_moneyness - m));
                iv_surface(tau_idx, mny_idx) = iv;
            end
        end

        % Accumulate
        valid_mask = ~isnan(iv_surface);
        iv_sum_surface(valid_mask) = iv_sum_surface(valid_mask) + iv_surface(valid_mask);
        iv_count_surface(valid_mask) = iv_count_surface(valid_mask) + 1;
    end

    % Compute average
    iv_avg_surface = iv_sum_surface ./ iv_count_surface;

    % Convert to table
    var_names = matlab.lang.makeValidName(string(all_moneyness));
    T_out = array2table(iv_avg_surface, 'VariableNames', var_names);
    T_out = addvars(T_out, all_tau', 'Before', 1, 'NewVariableNames', 'TTM');

    % Output path
    plot_save_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/IV_surface_average/";
    if ~exist(plot_save_path, 'dir')
        mkdir(plot_save_path);
    end

    % Filename
    if cid == 0
        fname = "IV_surface_average_HV.csv";
    elseif cid == 1
        fname = "IV_surface_average_LV.csv";
    else
        fname = "IV_surface_average_overall.csv";
    end
    writetable(T_out, fullfile(plot_save_path, fname));
end