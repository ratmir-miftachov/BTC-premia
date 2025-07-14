

% This file is to plot lower bounds in MATLAB to be consistent with other
% plots format

%% load data
clear,clc
addpath("m_Files_Color")                 % Add directory to MATLAB's search path for custom color files
addpath("m_Files_Color/colormap")        % Add subdirectory for colormap files
[~,~,~]=mkdir("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/"); % Create directory for output, if it doesn't exist

% Read lower bounds of Martin's bounds, Chabi-Yo and Loudis's restricted
% lower bounds and unrestricted lower bounds (based on preference)
MB = readtable("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Martin_LB.csv");
RLB = readtable("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Chabi-Yo_RLB.csv");
ULB = readtable("Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Chabi-Yo_ULB.csv");

%% PLot lower bounds with MB, ULB and RLB
% Focus on TTM 27
shadow_x_negative = [-0.6, -0.2];
shadow_x_positive = [0.2, 0.6];

% Create the figure
figure('Position', [100, 100, 800, 600]);

plot(MB.Date, MB.Lower_Bound * 100,'-','Color','r','LineWidth',2);hold on
plot(ULB.Date,ULB.Lower_Bound * 100,'-','Color','b','LineWidth',2);
plot(RLB.Date,RLB.Lower_Bound * 100,'-','Color','g','LineWidth',2);
hold off
% grid on
legend(["Martin","ULB","RLB"],'FontSize',15,'Location','northwest','Interpreter','latex','Box','off')

% Formatting the x-axis with yearly intervals
years = datetime(2017:2022, 1, 1);
xticks(years);

% years = datetime(2017:2022, 1, 1);
% ax = gca;                           % 取当前坐标轴
% ax.XTick = years;                   % 直接给 datetime
% ax.XTickFormat = 'yyyy';            % 只显示年份

% yrs = datenum(2017:2022, 1, 1);
% xticks(yrs);

% Set x-axis limits
xlim([datetime(2017, 07, 01) datetime(2022, 12, 17)]);

% Set y-axis limits
ylim([0, 300])

% Add labels and title
xlabel('Date', 'FontSize', 18);
ylabel('Annualized Lower Bound (%)', 'FontSize', 18);
title('Time-Varying Lower Bound of Bitcoin Premium (BP)', 'FontSize', 18);

% Rotate x-tick labels for better readability
xtickangle(45);

% Add a legend
legend('Martin (2017) Lower Bound', 'Chabi-Yo & Loudis (2020) Unrestricted Lower Bound', ...
    'Chabi-Yo & Loudis (2020) Restricted Lower Bound', 'FontSize', 12);

xlabel('Return','FontSize',15)
% ylabel('PK','FontSize',15)
set(gcf,'Position',[0,0,450,300]);  
ax = gca;
ax.FontSize = 15;
% ax.YAxis.FontWeight = 'bold'; % Make Y-axis tick labels bold
ax.YAxis.LineWidth = 1; % Increase the line width of the Y-axis
ax.XAxis.LineWidth = 1; % Increase the line width of the Y-axis
saveas(gcf,"Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Martin_Chabi-Yo_RLB_Preference_LB_MATLAB.png")

%% PLot lower bounds with only MB and RLB
% Focus on TTM 27
shadow_x_negative = [-0.6, -0.2];
shadow_x_positive = [0.2, 0.6];

% Create the figure
figure('Position', [100, 100, 800, 600]);

plot(MB.Date, MB.Lower_Bound * 100,'-','Color',[0.4667    0.5333    0.6000],'LineWidth',2);hold on
plot(RLB.Date,RLB.Lower_Bound * 100,'-','Color',[0.2745    0.5098    0.7059],'LineWidth',2);
hold off
% grid on
legend(["Martin","ULB","RLB"],'FontSize',15,'Location','northwest','Interpreter','latex','Box','off')

% Formatting the x-axis with yearly intervals
years = datetime(2017:2022, 1, 1);
xticks(years);

% years = datetime(2017:2022, 1, 1);
% ax = gca;                           % 取当前坐标轴
% ax.XTick = years;                   % 直接给 datetime
% ax.XTickFormat = 'yyyy';            % 只显示年份

% yrs = datenum(2017:2022, 1, 1);
% xticks(yrs);

% Set x-axis limits
xlim([datetime(2017, 07, 01) datetime(2022, 12, 17)]);

% Set y-axis limits
ylim([0, 349])

% Add labels and title
% xlabel('Date', 'FontSize', 18);
ylabel('Annualized Lower Bound (%)', 'FontSize', 18);
% title('Time-Varying Lower Bound of Bitcoin Premium (BP)', 'FontSize', 18);

% % Rotate x-tick labels for better readability
% xtickangle(45);

% Add a legend
legend('Martin (2017)', 'Chabi-Yo and Loudis (2020)', 'FontSize', 12, 'box', 'on', 'location', 'northeast');

% ylabel('PK','FontSize',15)
set(gcf,'Position',[0,0,450,300]);  
ax = gca;
ax.FontSize = 15;
% ax.YAxis.FontWeight = 'bold'; % Make Y-axis tick labels bold
ax.YAxis.LineWidth = 1; % Increase the line width of the Y-axis
ax.XAxis.LineWidth = 1; % Increase the line width of the Y-axis
saveas(gcf,"Lower_Bound/Tau-independent/unique/moneyness_step_0d01/multivariate_clustering_9_27_45/Martin_Chabi-Yo_RLB_Preference_LB_MATLAB.png")
