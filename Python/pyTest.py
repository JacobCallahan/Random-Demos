import sys

"""
ok, guys... so this is a quick little program that will take in a
text file and output the contents shifted over two alphabetic spaces
"""

changeLetter = {"a" : "y",
				"b" : "z",
				"c" : "a",
				"d" : "b",
	            "e" : "c",
	            "f" : "d",
	            "g" : "e",
	            "h" : "f",
	            "i" : "g",
	            "j" : "h",
	            "k" : "i",
	            "l" : "j",
	            "m" : "k",
	            "n" : "l",
	            "o" : "m",
	            "p" : "n",
	            "q" : "o",
	            "r" : "p",
	            "s" : "q",
	            "t" : "r",
	            "u" : "s",
	            "v" : "t",
	            "w" : "u",
	            "x" : "v",
	            "y" : "w",
	            "z" : "x",
	            ")" : ")",
	            "(" : "(",
	            "." : ".",
	            " " : " ",
	            "'" : "'",
}

with open("code.txt","r") as inFile:
  translatedText = ""
  while True:
    char = inFile.read(1)
    if not char:
      print ("Done!")
      break
    translatedText = translatedText + changeLetter[char.lower()]

print (translatedText)



	
	