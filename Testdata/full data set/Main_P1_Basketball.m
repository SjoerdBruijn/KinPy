close all;clear;format compact;
addpath(genpath('=VU 3D model='));

%% restore old matlab colormap and hold function
addpath(genpath('fix hold'));% hold function is adapted (see hold function current folder) such that the color order index is not reset (new plot starts with blue again)
set(groot,'defaultAxesColorOrder',[0 0 1;0 0.5 0;1 0 0;0 0.75 0.75;0.75 0 0.75;0.75 0.75 0;0.25 0.25 0.25])

%% Default plot settings (you can chnge these)
set(0,'defaultLineLineWidth',1.5);
set(0,'defaultAxesLineWidth',1.5)
set(0,'defaultAxesFontSize',12)

%% Load settings from excel sheet
settings                  = xlsreadsettings('Settings_Basketball.xls');
settings.data_path        = ['raw data', filesep]; %location of the data
settings.file_prefix      = 'TN000'; 
settings.file_extension   = '.ndf';
settings.pointer_file     = 'RB-06114.RIG';
settings.pointer_kol      = 13:18;
% filter settings
settings.filter_on                  = 1;   %1=on 0=off
settings.sample_frequency_opto      = 100;
settings.sample_frequency_fp        = 800;
settings.cutoff_frequency           = 30;
settings.maximum_interlopation_gap  = 0;
% pointer trial numbers
settings.reference_trial_nr     = 89; 
settings.cluster_pointer_nr     = 78:88; 
settings.forceplate_pointers_nr = 12:16;

%% calculation of bony landmarks (BLMs) with respect to marker clusters using on pointer trials
BLM = pointer2blm(settings.cluster_pointer_nr,settings.reference_trial_nr,settings.data_path,settings);
BLM.segment(2).blm_name = {'LM','SPH','LFE','MFE'};
plot_3d(BLM);

%% Calculating anatomical coordinate systems based during calibration posture
CP  = blm2cp(BLM); %CP = calibration posture
plot_3d(CP);

%% Calculating forceplate position/orientation based on forceplate pointers
FPpos           = pointer2FPpos(settings.forceplate_pointers_nr,settings.data_path,settings,0); %forceplate pointers
SO(1).points    = FPpos.corners;
SO(1).R         = FPpos.R;
SO(1).object    = 1;
plot_3d(CP,SO);

%% Calculate Calf coordinate system (ACSs) and inertial parameters in the cell below


%(Write here your code for: Step 2 Building your own anatomical function )


%% ------------------------------------------------------------------------
settings.file_no    = 114;
[x, y, z]           = load_optotrak_data(settings);
[Fext, Mext, CoP]   = load_kistler_FP_data(settings,FPpos,x);
traj                = trajcalc(CP,x,y,z);
traj.segment(1).axis_function   = 'calc_foot_antro_zat';
traj.segment(2).axis_function   = 'calc_calf_antro_zat';
traj.BerendBotje    = 1;

plot_3d(traj,SO,Fext,CoP,settings.sample_frequency_opto,[-1 1 0 1 -.3 1.5],[],Fext);

%% calculate Ankle moments below
