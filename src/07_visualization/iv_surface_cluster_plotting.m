addpath("m_Files_Color/colormap/")

% Load data

// % Load the common dates of the multivariate clustering
// common_dates_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/common_dates_cluster.csv"
// common_dates = pd.read_csv(common_dates_path)

// dates_Q = {}
// dates_Q[0] = common_dates[common_dates['Cluster']==0]['Date']
// dates_Q[1] = common_dates[common_dates['Cluster']==1]['Date']

// dates_Q_overall = pd.concat([dates_Q[0], dates_Q[1]])
// dates_Q_overall = pd.to_datetime(dates_Q_overall)
// dates_Q_overall = dates_Q_overall.sort_values()

% Load the common dates of the multivariate clustering
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

%% Overall
IV_surface_path = "Clustering/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/IV_surface_average/IV_surface_average_overall.csv";
data = readmatrix(IV_surface_path);

X = data(2:2:end,1); % TTM
Y = data(1,2:3:end); % Return
Z = data(2:2:end,2:3:end);

% Create a grid for x and y coordinates
[x, y] = meshgrid(Y, X);

% Plot the 3-D surface
figure;
surf(x, y, Z, 'FaceAlpha', 0.9);hold on % Creates the 3-D surface plot

% Apply lighting to the surface
%light; lighting phong; % Adjust the lighting to enhance surface visibility
%material shiny; % Adjust material properties to make the surface more reflective


% Apply a rainbow colormap
map = hsv;
colormap(map); % This produces a rainbow-like color scheme
plot3(data(1,2:end),ones(size(data(1,2:end)))*27,data(28,2:end),'k','LineWidth',4)

% Add labels and title
xlabel('Return');
ylabel('\tau','Interpreter','tex');
zlabel('IV');
xlim([-0.15,0.15])
ylim([3,60])
zlim([0.5,1.2])
xticks([-0.15,0,0.15])
yticks([3,27,60])
zticks([0.6, 0.8, 1, 1.2])
% title('Overall');

ax = gca;
ax.FontSize = 15;
% ax.YAxis.FontWeight = 'bold'; % Make Y-axis tick labels bold
ax.YAxis.LineWidth = 1; % Increase the line width of the Y-axis
ax.XAxis.LineWidth = 1; % Increase the line width of the Y-axis

% Adjust the view angle for better visualization
view(45, 10); % Adjusts the viewing angle of the plot

set(gcf,'position',[0,0,450,300])
saveas(gcf,"IV_surface/IV_surface_1by3_2_OA.png")
%% HV Cluster
data = readmatrix('IV_surface/average_surface0.csv');


X = data(2:2:end,1); % TTM
Y = data(1,2:3:end); % Return
Z = data(2:2:end,2:3:end);

% Create a grid for x and y coordinates
[x, y] = meshgrid(Y, X);

% Plot the 3-D surface
figure; % Opens a new figure window
surf(x, y, Z, 'FaceAlpha', 0.9);hold on % Creates the 3-D surface plot

% Apply lighting to the surface
%light; lighting phong; % Adjust the lighting to enhance surface visibility
%material shiny; % Adjust material properties to make the surface more reflective


% Apply a rainbow colormap
colormap(map); % This produces a rainbow-like color scheme
plot3(data(1,2:end),ones(size(data(1,2:end)))*27,data(28,2:end),'k','LineWidth',4)


% Add labels and title
xlabel('Return');
ylabel('\tau','Interpreter','tex');
zlabel('IV');
xlim([-0.15,0.15])
ylim([3,60])
zlim([0.5,1.2])
xticks([-0.15,0,0.15])
yticks([3,27,60])
zticks([0.6, 0.8, 1, 1.2])
% title('HV');

ax = gca;
ax.FontSize = 15;
% ax.YAxis.FontWeight = 'bold'; % Make Y-axis tick labels bold
ax.YAxis.LineWidth = 1; % Increase the line width of the Y-axis
ax.XAxis.LineWidth = 1; % Increase the line width of the Y-axis

% Adjust the view angle for better visualization
view(45, 10); % Adjusts the viewing angle of the plot

set(gcf,'position',[0,0,450,300])
saveas(gcf,"IV_surface/IV_surface_1by3_2_HV.png")
%% LV Cluster
data = readmatrix('IV_surface/average_surface1.csv');


X = data(2:2:end,1); % TTM
Y = data(1,2:3:end); % Return
Z = data(2:2:end,2:3:end);

% Create a grid for x and y coordinates
[x, y] = meshgrid(Y, X);

% Plot the 3-D surface
figure;
surf(x, y, Z, 'FaceAlpha', 0.9);hold on % Creates the 3-D surface plot

% Apply lighting to the surface
%light; lighting phong; % Adjust the lighting to enhance surface visibility
%material shiny; % Adjust material properties to make the surface more reflective

% Apply a rainbow colormap
colormap(map); % This produces a rainbow-like color scheme
plot3(data(1,2:end),ones(size(data(1,2:end)))*27,data(28,2:end),'k','LineWidth',4)

% Add labels and title
xlabel('Return');
ylabel('\tau','Interpreter','tex');
zlabel('IV');
xlim([-0.15,0.15])
ylim([3,60])
zlim([0.5,1.2])
xticks([-0.15,0,0.15])
yticks([3,27,60])
zticks([0.6, 0.8, 1, 1.2])
% title('LV');

ax = gca;
ax.FontSize = 15;
% ax.YAxis.FontWeight = 'bold'; % Make Y-axis tick labels bold
ax.YAxis.LineWidth = 1; % Increase the line width of the Y-axis
ax.XAxis.LineWidth = 1; % Increase the line width of the Y-axis

% Adjust the view angle for better visualization
view(45, 10); % Adjusts the viewing angle of the plot

set(gcf,'position',[0,0,450,300])
saveas(gcf,"IV_surface/IV_surface_1by3_2_LV.png")






