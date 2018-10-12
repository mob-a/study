import cymecab

texts = [
    "ばねとは、力が加わると変形し、力を取り除くと元に戻るという、物体の弾性という性質を利用する機械要素である。",
    "広義には、弾性の利用を主な目的とするものの総称ともいえる。",
    "ばねの形状や材質は様々で、日用品から車両、電気電子機器、構造物に至るまで、非常に多岐にわたって使用される。",
]

cmw = cymecab.CyMeCabWrapper()
for text in texts:
    print(text)
    cmw.parse(text)
    print(cmw.words)
