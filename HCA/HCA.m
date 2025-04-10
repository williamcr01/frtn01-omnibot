clc
clear
%Parameters
fs = 1000;
t = 0:1/fs:2;
x = cos(2*pi*5*t) + 0.5*sin(2*pi*10*t); % Test signal

T = 0.5;
H = 5;

X_harmonic = harmonic_array(x, t, T, H);           % Extract harmonics
x_rebuilt = harmonic_assembler(X_harmonic, t, T);  % Reconstruct signal

figure;
plot(t, x, 'b', t, x_rebuilt, 'r--');
legend('Original', 'Reconstructed');
xlabel('Time (s)');
ylabel('x(t)');
title('Harmonic Extraction and Reconstruction');

%Disperser
function X_harmonic = harmonic_array(x, t, T, H)
omega = 2*pi/T;
%x - signal (vector)
%t - time vector
%T - time window
%H - number of harmonic elements

X_harmonic = zeros(H+1, length(t));
for k = 1:length(t)
    tk = t(k);
    idx = t >= (tk -T) & t <= tk;
    tau = t(idx);
    x_segment = x(idx);

    for h = 0:H
        exponential = exp(-1j * h * omega * tau);
        integral = trapz(tau, x_segment .* exponential);
        X_harmonic(h + 1, k) = (1/T)*integral;
    end
end
end

%Assembler
function X_reconstructed = harmonic_assembler(X_harmonic, t, T)
omega = 2*pi/T;
%X_harmonic - matrix of harmonic components
%t - time vector
%T - time window used in harmonic extraction

H = size(X_harmonic, 1) - 1;

X_reconstructed = zeros(1, length(t));

for k = 1:length(t)
    tk = t(k);
    sum_val = 0;
    for h = -H:H
        idx = abs(h); %index into X_harmonic (0-based indexing correction)
        if h < 0
            Xh = conj(X_harmonic(idx + 1, k));
        else
            Xh = X_harmonic(h + 1, k);
        end
        sum_val = sum_val + Xh * exp(1j * h * omega * tk);
    end
    X_reconstructed(k) = real(sum_val); %optional taking of real part

end
end

