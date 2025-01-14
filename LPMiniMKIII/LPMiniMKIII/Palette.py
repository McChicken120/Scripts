Pink_Shades = [52, 54, 55, 71, 82, 94, 95, 107]

White_Shades = [1, 3, 103, 112, 114, 115, 117, 118, 119]

Red_Shades = [5, 6, 7, 57, 58, 59, 106, 120]

Beige_Shades = [12, 70, 105, 109]

Orange_Brown_Shades = [9, 10, 11, 60, 62, 84, 96, 99, 108, 125, 126, 127]

Yellow_Shades = [14, 15, 74, 97]

Mint_Shades = [20, 24, 28, 29, 30, 31, 33, 34, 35, 65, 68, 77, 88, 101, 102]

Green_Shades = [18, 19, 21, 22, 23, 25, 26, 27, 63, 73, 75, 76, 85]

Green_Shades_Two =  [32, 36, 37, 38, 86, 87, 98, 110, 111, 122, 123]

Blue_Shades = [40, 42, 43, 46, 47, 66, 67, 79, 92, 104]

Purple_Shades = [48, 50, 51, 69, 81, 93, 116]

Shades = [Pink_Shades, White_Shades, Red_Shades, Beige_Shades, Orange_Brown_Shades, Yellow_Shades, Mint_Shades, Green_Shades, Green_Shades_Two, Blue_Shades, Purple_Shades]
Shade_Names = ["Pink", "White", "Red", "Beige", "Orange/Brown", "Yellow", "Mint", "Green", "Blue", "Purple"]

Removed = [56, 61, 100, 8, 124, 17, 89, 90,
 91, 46, 44, 81, 54, 3, 72, 84,
 83, 13, 16, 64, 39, 78, 41, 45,
 80, 49, 53, 2, 121, 4, 105, 113, 73,
 111, 85, 114, 32, 36, 70, 103, 115,
 117, 82, 96, 10, 12, 125, 15, 40,
 92, 42, 104, 112, 71, 59, 1, 7,
 127, 11, 62, 63, 19, 68, 38, 47,
 67, 43, 55, 58, 0]

#for shade in Shades:
 #   for value in shade:
  #      if value in Removed:
   #         shade.remove(value)
    #print(str(len(shade)))

print(str(len(Removed)))

Removed.sort()

print(str(Removed))
