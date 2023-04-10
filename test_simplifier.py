from simplertimes import simplify

# Create the ACCESS simplifier model
access_simplifier = simplify.create_simplifier()

access_simplifier.print_details()

# to_simplify = [
#     "The Palestinian Authority formally becomes the 123rd member of the International Criminal Court .<n>The move gives the court jurisdiction over alleged crimes in Palestinian territories .<n>Palestinians signed the ICC's founding Rome Statute in January .",
#     'Theia, a white-and-black bully breed mix, was apparently hit by a car and buried in a field .<n>Four days later, the dog staggers to a farm and is taken in by a worker .<n>She needs surgery to fix a dislocated jaw and a caved-in sinus cavity .',
#     "Mohammad Javad Zarif is the Iranian foreign minister .<n>He is the opposite number in talks with the U.S. over Iran's nuclear program .<n>He received a hero's welcome as he arrived in Iran on a sunny Friday morning ."
# ]

to_simplify = [
    "The Palestinian Authority becomes the 123rd member of the International Criminal Court. The move gives the court jurisdiction over alleged crimes in Palestinian territories. Israel and the United States opposed the Palestinians' efforts to join the body. But Palestinian Foreign Minister Riad al-Malki said it was a move toward greater justice.",
    'Theia, a one-year-old bully breed mix, was hit by a car and buried in a field. She managed to stagger to a nearby farm, dirt-covered and emaciated. She suffered a dislocated jaw, leg injuries and a caved-in sinus cavity.',
    "Mohammad Javad Zarif is the Iranian foreign minister. He has been John Kerry's opposite number in securing a breakthrough in nuclear discussions. He received a hero's welcome as he arrived in Iran on a sunny Friday morning. But there are some facts about Zarif that are less well-known.",
    'Coach Michaels said, "The team did a hell of a play out there today."',
    'Testing "Quotation Marks"  (Are parenthesis okay?)'
]

simplified, comp_simp_pairs = access_simplifier.simplify_document(to_simplify)

# Nicely formatted output
for doc_idx in range(len(to_simplify)):
    print(f"============================================================")
    print()

    doc_simp = simplified[doc_idx]
    print(f"Summary:\n{doc_simp}\n")
    
    doc_sent_pairs = comp_simp_pairs[doc_idx]
    print(f"Simplifications:")
    for comp, simp in doc_sent_pairs:
        print(f"{comp}")
        print(f"--> {simp}")
    print()
    print(f"============================================================")

