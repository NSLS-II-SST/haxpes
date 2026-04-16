range1 = {
    "energymin": 1985,
    "energymax": 3250,
    "harmonic": 3,
    "crystal": "Si(111)"
}
range2 = {
    "energymin": 3250,
    "energymax": 3500,
    "harmonic": 3,
    "crystal": "Si(220)"
}
range3 = {
    "energymin": 3500,
    "energymax": 4500,
    "harmonic": 5,
    "crystal": "Si(220)"
}
range4 = {
    "energymin": 4500,
    "energymax": 6000,
    "harmonic": 7,
    "crystal": "Si(220)"
}
range5 = {
    "energymin": 6000,
    "energymax": 8000,
    "harmonic": 9,
    "crystal": "Si(333)"
}

dcmranges = [range1, range2, range3, range4, range5]

#offsetdict for setting the Bragg angle offsets for crystal pairs
offsetdict = {
    "Si(111)": 10.829,
    "Si(220)": 10.782,
    "Si(333)": 10.829,
    "Si(444)": 10.829,
    "xBe(020)": 10.782
}

#dictionary for setting the goniometer lateral possition for each crystal pair
gonilatdict = {
    "Si(111)": 0, 
    "Si(220)": 35, 
    "Si(333)": 0, 
    "Si(444)": 0,
    "xBe(020)": -30
}

#dictionary for setting the default x2roll position for each crystal pair
x2rolldict = {
    "Si(111)": -1.9, 
    "Si(220)": 0.5, 
    "Si(333)": -1.9, 
    "Si(444)": -1.9,
    "xBe(020)": -9.6
}
