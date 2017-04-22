import numpy as np
import matplotlib.pyplot as plt


def main():
    num_trials = 12
    video_capture_num_frames, video_capture_trial_time = np.loadtxt('opencv-video-capture-trials.txt', delimiter=',', unpack=True)
    video_stream_num_frames, video_stream_trial_time = np.loadtxt('threaded-video-stream-trials.txt', delimiter=',', unpack=True)
    plt.plot(np.arange(num_trials), video_capture_num_frames, 'ro')
    plt.plot(np.arange(num_trials), video_stream_num_frames, 'bo')
    plt.show()


if __name__ == '__main__':
    main()
