import numpy as np
from scipy.signal import butter, filtfilt
import warnings


class FilterLinearNoise(object):
    def __init__(self, samplerate=None):
        '''
        @params
        freqrange       (list) of the lower and upper frequency value to filter at
        samplerate      (int) the sampling rate in Hz
        '''
        # self.freqrange = np.array(freqrange)
        self.samplerate = samplerate
        if not samplerate:
            warnings.warn("User needs to pass in sample rate in Hz!")

    def __butthighpass(self, cut, order):
        # the Nyquist frequency
        nyq = self.samplerate/2.
        b, a = butter(N=order, Wn=cut, btype='highpass', analog=False)
        return b, a

    def __buttlowpass(self, cut, order):
        # the Nyquist frequency
        nyq = self.samplerate/2.
        b, a = butter(N=order, Wn=cut, btype='lowpass', analog=False)
        return b, a

    def __buttfilt(self, rawdata, freqrange, btype, order):
        # Butterworth filter wrapper function with zero phase distortion.
        # FUNCTION:
        #   y = buttfilt(dat,freqrange,samplerate,filttype,order)
        #
        # INPUT ARGS: (defaults shown):
        #   raw_data = dat;           % data to be filtered (if data is a matrix, BUTTFILT filters across rows)
        #   freqrange = [58 62];      % filter range (depends on type)
        #   filttype = 'stop';        % type of filter ('bandpass','low','high','stop')
        #   order = 4;                % order of the butterworth filter
        #   filters = {B,A};          % a set of filters to use on data (created by a previous buttfilt call)
        # OUTPUT ARGS::
        #   data = the filtered data
        # the Nyquist frequency
        nyq = self.samplerate/2.

        # create a butterworth filter with specified order, freqs, type
        b, a = butter(N=order, Wn=freqrange/nyq, btype=btype)
        filters = np.array((b, a))
        # run filtfilt for zero phase distortion
        data = filtfilt(b, a, rawdata)
        return data, filters

    def filter_rawdata(self, rawdata, freqrange, btype='bandpass', order=4):
        freqrange = np.asarray(freqrange)

        rawdata, filters = self.__buttfilt(rawdata=rawdata,
                                           freqrange=freqrange,
                                           btype=btype,
                                           order=order)
        return rawdata

    def notchlinenoise(self, rawdata, freq, filttype='notch', order=3):
        '''
        To run filtering of raw data that comes in as [numchans, numtime], it will
        apply freqrange and it's corresponding harmonics up to nyquist with a notch filter.

        Example usage:
        filtereddata = filterrawdata([59.5,60.5], samplerate=1000, filtttype='notch')

        Parameters:
        freqrange = [58 62];      % filter range (depends on type)
        filttype        (str) notch for now
        order = 4;                % order of the butterworth filter
        '''
        ######################### FILTERING ################################
        # define lambda function that creates an array of the frequency harmonic +/- 0.5 Hz
        def freqrange(multfactor): return np.array(
            [freq*multfactor - 0.5, freq*multfactor + 0.5])

        # perform notch filtering at line noise and its harmonics
        if filttype == 'notch':
            rawdata, filters = self.__buttfilt(
                rawdata, freqrange(1), 'bandstop', order=order)
            rawdata, _ = self.__buttfilt(
                rawdata, freqrange(2), 'bandstop', order=order)

            print("filtered at: ", freqrange(2))
            if self.samplerate > 250:
                rawdata, _ = self.__buttfilt(
                    rawdata, freqrange(3), 'bandstop', order=order)
                rawdata, _ = self.__buttfilt(
                    rawdata, freqrange(4), 'bandstop', order=order)

                print("filtered at: ", freqrange(3))
                print("filtered at: ", freqrange(4))
                if self.samplerate > 500 and self.samplerate > freqrange(5)[0]:
                    rawdata, _ = self.__buttfilt(
                        rawdata, freqrange(5), 'bandstop', order=order)
                    rawdata, _ = self.__buttfilt(
                        rawdata, freqrange(6), 'bandstop', order=order)
                    rawdata, _ = self.__buttfilt(
                        rawdata, freqrange(7), 'bandstop', order=order)
                    rawdata, _ = self.__buttfilt(
                        rawdata, freqrange(8), 'bandstop', order=order)
                    print("filtered at: ", freqrange(8))
        else:
            warnings.warn("No filtering done on raw data! Are you sure?")
        return rawdata


if __name__ == '__main__':
    linefreq = 60
    samplerate = 1024.

    filtlinenoise = FilterLinearNoise(samplerate=samplerate)

    # example run through sample data
    data = np.random.random(size=(5, 5000))
    print(data.shape)
    # to use a bandpass filter
    rawfiltrange = [0.1, 500]
    data = filtlinenoise.filter_rawdata(data, freqrange=rawfiltrange)

    # to notch at line noise
    data = filtlinenoise.notchlinenoise(data, freq=freqrange)

    print(data.shape)
