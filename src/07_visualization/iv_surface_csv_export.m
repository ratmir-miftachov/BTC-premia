% This file is to get average IV surface in both clusters, and stored in
% csv file

clc; clear; close all;

% ---------- Step 0: Load clustering dates ----------
common_dates_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/common_dates_cluster.csv";
T = readtable(common_dates_path); % Read CSV file as table

% Extract dates for HV Cluster and LV Cluster
dates_Q = containers.Map('KeyType', 'double', 'ValueType', 'any');
dates_Q(0) = T.Date(T.Cluster == 0);
dates_Q(1) = T.Date(T.Cluster == 1);

% Merge and sort all dates
dates_Q_overall = [dates_Q(0); dates_Q(1)];
dates_Q_overall = datetime(dates_Q_overall);  % Convert to datetime format
dates_Q_overall = sort(dates_Q_overall);      % Sort by

% ---------- Step 1: Load IV data ----------
% Set IV path
interpolated_iv_path = 'IV/IV_surface_SVI/Tau-independent/unique/moneyness_step_0d01/';
file_list = dir(fullfile(interpolated_iv_path, 'interpolated_*_allR2.csv'));

% Initialize variables
all_tau = 3:60;                                                  % maturities (TTM)
all_moneyness = -1:0.01:1;                                       % moneyness grid
iv_map = containers.Map('KeyType', 'char', 'ValueType', 'any');

% Initialize: used to accumulate all IV surfaces
iv_sum_surface = zeros(length(all_tau), length(all_moneyness));
iv_count_surface = zeros(length(all_tau), length(all_moneyness));  % Used for NaN mask counting

% Iterate over files
for k = 1:length(file_list)
    filename = fullfile(interpolated_iv_path, file_list(k).name);
    T = readtable(filename);
    % The first column is Date, the second column is TTM
    % The first row is moneyness (start from the third column)

    current_date = T{2,1};
    if ~ismember(current_date, dates_Q_overall)
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

    % Accumulate to the total surface
    valid_mask = ~isnan(iv_surface);
    iv_sum_surface(valid_mask) = iv_sum_surface(valid_mask) + iv_surface(valid_mask);
    iv_count_surface(valid_mask) = iv_count_surface(valid_mask) + 1;

end

% ---------- Step 2: Calculate average IV surface ----------
iv_avg_surface = iv_sum_surface ./ iv_count_surface;

% ---------- Step 3: Write to CSV ----------
% T_out = array2table(iv_avg_surface, 'VariableNames', ...
%     matlab.lang.makeValidName(strsplit(num2str(all_moneyness))));
T_out = array2table([all_moneyness;iv_avg_surface],'VariableNames', ...
    matlab.lang.makeValidName(string(all_moneyness)));
T_out = addvars(T_out, [nan;all_tau'], 'Before', 1, 'NewVariableNames', 'TTM');


plot_save_path = strcat('Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/IV_surface_average/');
if ~exist(plot_save_path , 'dir')
    mkdir(plot_save_path );
end
writetable(T_out, strcat(plot_save_path, 'IV_surface_average_overall.csv'));

