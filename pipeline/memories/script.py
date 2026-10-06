"""'Yaadein' reel - script in Roman Urdu / Hinglish with word timings (seconds) from Whisper large-v3
(Hindi + Urdu passes cross-checked). '*' marks a keyword (orange serif italic in the captions)."""

LINES = [
    [('Jaise', 0.76), ('bhi', 1.28), ('*yaadon', 1.50), ('ko', 2.00), ('*bhulana', 2.16), ('aasaan', 2.50),
     ('nahi', 2.78)],
    [('*Purani', 3.84), ('*yaadon', 4.36), ('ko', 4.80), ('bhulane', 4.86), ('mein', 5.20), ('humein', 5.38),
     ('*mushkil', 5.60), ('hoti', 5.96), ('hai,', 6.18), ('kyunki', 6.34)],
    [('humein', 8.22), ('lagta', 8.74), ('hai', 9.00), ('ki', 9.16), ('wo', 9.42), ('hamari', 10.42),
     ('*khushi', 10.82), ('ke', 11.78), ('*pal', 11.98), ('the', 12.18)],
    [('par', 12.34), ('*asal', 12.56), ('mein', 12.72), ('ye', 14.60), ('*sach', 15.12), ('*nahi', 15.40),
     ('hai', 15.62)],
    [('Aane', 19.74), ('wale', 20.26), ('*kal', 20.48), ('ke', 20.78), ('liye', 20.94), ('hamare', 21.02),
     ('*aaj', 21.30), ('ko', 21.50), ('*dafnana', 21.72), ('hoga', 22.14)],
]
DURATION = 27.84
