%% calling network state from Matlab
clear
clc
close all
% Change the current folder to the folder of this m-file.
if(~isdeployed)
  cd(fileparts(which(mfilename)));
end
cd ..
cd ..
fig_folder=[pwd '\Matlab\matlab_results\figs\'];

%% loading data
lfp = readNPY([pwd '\data\Extra.npy']); % you need to clone this to read a npy: https://github.com/kwikteam/npy-matlab
dt_mat=readNPY([pwd '\data\dt.npy']); 
% converting in python-compatible classes
dt=py.numpy.array(dt_mat);
data_extra=py.numpy.array(lfp);
data = py.dict(pyargs('Channel_Keys','Extra','dt',dt,'Extra',data_extra));
% parameters
N_wavelets=5;
f0=72.2;
w0=1.8;
gain = 1;
Vext_key='Extra';
freqs = py.numpy.linspace(f0/w0, f0*w0, N_wavelets);
new_dt = 5e-3;
smoothing=43e-3;
% run preprocessing
py.src.functions.preprocess_LFP(data, freqs, new_dt, Vext_key , gain, smoothing);

Tstate=0.4; % 400 ms
alpha=2.8;
T_sliding_mean=0.5; % 500 ms
% run NSI computation
py.src.functions.compute_Network_State_Index(data, 'pLFP', freqs, Tstate, alpha, T_sliding_mean);

%% now the "data" dictionary contains the "NSI" and "pLFP" variables
time_s_lfp=(1:1:length(lfp))*double(dt);
pLFP=double(data{'pLFP'});
NSI=double(data{'NSI'});
time_s_pLFP=(1:1:length(pLFP))*new_dt;

%% plot LFP, pLFP, NSI
figure
h(1)=subplot(3,1,1);
plot(time_s_lfp,double(data{'Extra'}))
title('original LFP')
h(2)=subplot(3,1,2);
plot(time_s_pLFP,pLFP)
title('pLFP')
h(3)=subplot(3,1,3);
plot(time_s_pLFP,NSI)
title('NSI')
xlabel('time [s]')
linkaxes(h,'x')

%% histogram NSI occurrences
figure
histogram(NSI,'normalization','probability')
xlabel('NSI')
ylabel('probability')



