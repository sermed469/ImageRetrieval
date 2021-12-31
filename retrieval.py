from PIL import Image
import math

class Pixel:
    
    def __init__(self,R,G,B):
        self.R = R
        self.G = G
        self.B = B

def getPixels(img,image,images_hsv):
    column, row = img.size

    pixels = list(img.getdata())
    
    if(type(pixels[0]) == int):#Eğer resim gri seviyesinde ise 
        count = 0
        for p in pixels:
            p = (p,p,p)
            pixels[count] = p
            count += 1
    
    pixelss = []
    
    for pixel in pixels:#R,G,B değerlerini içeren nesne dizisi oluşturulur
        pixelss.append(Pixel(pixel[0],pixel[1],pixel[2]))
        
    for i in range(row):#piksel değerlerini içeren liste matris haline çevrilir
        r = []
        temp = []
        for j in range(column):
           r.append(pixelss[(i*(column))+j])
           temp.append(0)
        image.append(r)
        images_hsv.append(temp)
    
def calculateHue(img,image,images_hsv):
    
    column, row = img.size
    
    for i in range(row):
        for j in range(column):
            
            r = image[i][j].R
            g = image[i][j].G
            b = image[i][j].B

            if((image[i][j].R == image[i][j].G) and (image[i][j].R == image[i][j].B)):#R,G,B değerleri eşit ise
                a = 0.0
            else:
                a = math.acos((((r - g) + (r - b)) / 2)/(math.sqrt((math.pow(r - g,2)) + ((r - b) * (g - b)))))

            a = a * (180.0 / (math.pi))#radyan değeri dereceye dönüştürülür
            
            if(image[i][j].B > image[i][j].G):
                a = 360.0 - a

            images_hsv[i][j] = round(a)

def calculateHistograms(img,image,images_hsv):
    
    column, row = img.size
    
    histR = []
    histG = []
    histB = []
    histH = []
    
    for i in range(256):
        histR.append(0)
        histG.append(0)
        histB.append(0)
    
    for i in range(361):
        histH.append(0)
    
    for i in range(row):
        for j in range(column):
            histR[image[i][j].R] += 1
            histG[image[i][j].G] += 1
            histB[image[i][j].B] += 1
            histH[images_hsv[i][j]] += 1
    
    for i in range(256):#R,G ve B histogramlarının normalize edilmesi

        histR[i] /= row * column
        histG[i] /= row * column
        histB[i] /= row * column
        
    for i in range(361):#H histogramının normalize edilmesi   
        histH[i] /= row * column
    
    return [histR,histG,histB,histH]

def calculateEuclideanDistance(train,test):
    
    test_distance = []
    
    for t1 in test:#test resimlerinin eğitim resimlerine olan mesafelerinin hesaplanması
        dist = []
        for t2 in train:
            dist.append([distance(t1[0],t2[0]),
                         distance(t1[1],t2[1]),
                         distance(t1[2],t2[2]),
                         distance(t1[3],t2[3])])
        
        test_distance.append(dist)   
    
    return test_distance
    
def distance(hist1,hist2):
    
    size = len(hist1)
    dist = 0
    
    for i in range(size):
        dist += math.pow((hist1[i] - hist2[i]), 2)
    
    dist = math.sqrt(dist)    
    
    return dist

def findFiveSimilarImages(results):
    
    distanceRGB = []
    distanceHSV = []

    for i in range(60):#bütün test resimleri için
        temp1 = []
        temp2 = []
        for j in range(120):#tüm eğitim resimlerine olan mesafe
            temp1.append(results[i][j][0] + results[i][j][1] + results[i][j][2])#RGB uzayında
            temp2.append(results[i][j][3])#HSV uzayında
        distanceRGB.append(temp1)
        distanceHSV.append(temp2)
        
    sim_imgRGB = []
    sim_imgHSV = []
    
    dist1 = []#RGB uzayında uzaklıkların saklanacağı liste
    dist2 = []#H değeri için uzaklıkların saklanacağı liste
    
    for i in range(60):#uzaklıkların geçici olarak saklanacağı matrislerin oluşturulması
        temp3 = []
        temp4 = []
        for j in range(120):
            temp3.append(distanceRGB[i][j])
            temp4.append(distanceHSV[i][j])
        dist1.append(temp3)
        dist2.append(temp4)
        
    for i in range(60):#bütün test resimleri için
        five_imgRGB = []
        five_imgHSV = []
        for j in range(5):
            
            min_value = min(dist1[i])#minimum uzaklık bulunur
            min_index = distanceRGB[i].index(min_value)#uzaklığın hangi resimle olduğu bulunur
            five_imgRGB.append({"value" : min_value, "index" : min_index})#uzaklık ve resim bilgisi dict olarak listeye eklenir
            dist1[i].remove(min_value)
            
            min_value = min(dist2[i])
            min_index = distanceHSV[i].index(min_value)
            five_imgHSV.append({"value" : min_value, "index" : min_index}) 
            dist2[i].remove(min_value)
        
        sim_imgRGB.append(five_imgRGB)
        sim_imgHSV.append(five_imgHSV)
    
    return sim_imgRGB,sim_imgHSV
        
animals = ["elephant","flamingo","kangaroo","leopards","octopus","sea_horse"]

train = []#eğitim resimlerinin histogramlarının saklanacağı liste
for i in range(6):#her bir resim türü için
    temp = []

    for j in range(1,21):#tüm eğitim resimleri için
        
        if(j < 10):
            img = Image.open("images/" + animals[i] + "/image_000"+str(j)+".jpg") 
        else:
            img = Image.open("images/" + animals[i] + "/image_00"+str(j)+".jpg") 
        image = []
        images_hsv = []
        getPixels(img,image,images_hsv)
        calculateHue(img,image,images_hsv)
        train.append(calculateHistograms(img,image,images_hsv))

test = []
for i in range(6):#her bir resim türü için
    for j in range(21,31):#tüm test resimleri için
        img = Image.open("images/" + animals[i] + "/image_00"+str(j)+".jpg") 
        image = []
        images_hsv = []
        getPixels(img,image,images_hsv)
        calculateHue(img,image,images_hsv)
        test.append(calculateHistograms(img,image,images_hsv))
    
results = calculateEuclideanDistance(train,test)

sim1, sim2 = findFiveSimilarImages(results)
count = 0
count1 = 0
similar1 = []
similar2 = []
for i in range(60):
    temp1 = []
    temp2 = []

    for j in range(5):

        temp1.append(animals[int(sim1[i][j]['index'] / 20)] + "/image_00" + str((sim1[i][j]['index'] % 20) + 1))
        temp2.append(animals[int(sim2[i][j]['index'] / 20)] + "/image_00" + str((sim2[i][j]['index'] % 20) + 1))
    
    similar1.append((animals[int(i / 10)] + "/image_00" + str((i % 10) + 1 + 20),temp1))
    similar2.append((animals[int(i / 10)] + "/image_00" + str((i % 10) + 1 + 20),temp2))

print("RGB")    
for img in similar1:
    print("most similar images of " + str(img[0]) + ": " + img[1][0] + ", " + img[1][1] + ", " + img[1][2] + ", " + img[1][3] + ", " + img[1][4])

print("HSV")
for img in similar2:
    print("most similar images of " + str(img[0]) + ": " + img[1][0] + ", " + img[1][1] + ", " + img[1][2] + ", " + img[1][3] + ", " + img[1][4])
