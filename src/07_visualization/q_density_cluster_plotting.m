%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Set workingpath
work_path = "/Users/irtg/Documents/Github/BTC-premia/SVI_independent_tau/";
cd(work_path);

% Read cluster information
cluster_file = fullfile("Clustering", "Tau-independent", "unique", ...
    "moneyness_step_0d01", "multivariate_clustering_9_27_45", "common_dates_cluster.csv");
T = readtable(cluster_file);
dates_Q = containers.Map({0, 1}, {string(T.Date(T.Cluster==0)), string(T.Date(T.Cluster==1))});

% Set parameters
ttm_to_plot = 27;
q_dir = fullfile(work_path, "Q_from_pure_SVI", "Tau-independent", "unique", ...
    "moneyness_step_0d01", sprintf("tau_%d", ttm_to_plot));

plot_save_dir = fullfile(work_path, "Q_plots", "Tau-independent", "unique", ...
    "moneyness_step_0d01", "Q_density_average_plot", ...
    sprintf("tau_%d", ttm_to_plot), "multivariate_clustering_9_27_45");
if ~exist(plot_save_dir, 'dir')
    mkdir(plot_save_dir);
end

% Get all Q density files
files = dir(fullfile(q_dir, "*.csv"));

% Initialize
cluster_q_curves = containers.Map({0, 1}, {[], []});
cluster_common_m = containers.Map('KeyType','double','ValueType','any');

for i = 1:length(files)
    fname = files(i).name;
    fpath = fullfile(q_dir, fname);

    % 提取日期
    parts = split(fname, '_');
    if length(parts) < 3, continue; end
    date_str = erase(parts{3}, ".csv");

    % 判断属于哪个cluster
    if ismember(date_str, dates_Q(0))
        cid = 0;
    elseif ismember(date_str, dates_Q(1))
        cid = 1;
    else
        continue;
    end

    % 读取Q密度数据
    Q = readtable(fpath);
    if ~all(ismember(["m", "spdy"], Q.Properties.VariableNames))
        continue;
    end

    [sorted_m, idx] = sort(Q.m);
    sorted_q = Q.spdy(idx);

    % 存储
    if ~isKey(cluster_common_m, cid)
        cluster_common_m(cid) = sorted_m;
    end
    cluster_q_curves(cid) = [cluster_q_curves(cid); sorted_q'];
end

% Plot Q density
for cid = [0, 1]
    m_vals = cluster_common_m(cid);
    Q_mat = cluster_q_curves(cid);
    avg_q = mean(Q_mat, 1, 'omitnan');

    % 绘图
    figure('Position', [0,0,450,300]);
    hold on;
    for k = 1:size(Q_mat,1)
        plot(m_vals, Q_mat(k,:), 'Color', [0.6, 0.6, 0.6], 'LineWidth', 0.5, 'LineStyle', '-');
    end
    plot(m_vals, avg_q, 'k-', 'LineWidth', 2);

    xlabel('Moneyness');
    ylabel('Q Density');
    xlim([-0.15, 0.15]);
    ylim([min(avg_q)-0.01, max(avg_q)+0.01]);
    set(gca, 'FontSize', 15);
    set(gca, 'XTick', [-0.15 0 0.15]);
    box on;

    if cid == 0
        fname_out = "Q_density_tau_27_HV.png";
    else
        fname_out = "Q_density_tau_27_LV.png";
    end
    saveas(gcf, fullfile(plot_save_dir, fname_out));
end