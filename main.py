import boto3

# Inicializa os serviços da s3 (armazenar), e o rekognition (identificar)
s3 = boto3.resource('s3')
client = boto3.client('rekognition')

def lista_imagens():
    imagens=[]

    bucket = s3.Bucket('chris-face-images') #fa-imagens é o bucket de referência
    for imagem in bucket.objects.all():
        imagens.append(imagem.key)
    print(imagens)

    return imagens

# Caso queira uma nova coleção
def criar_colecao(nome):
    response=client.create_collection(
        CollectionId=nome
        )

# Indexa todas as imagens presentes no bucket e coloca numa collection
def indexa_colecao(imagens, nome):
    for i in imagens:
        response=client.index_faces(
            #Coleções que guardam as imagens
            CollectionId=nome,
            DetectionAttributes=[],
            ExternalImageId=i[:-4], #remove o ".png"
            Image={
                'S3Object': {
                    'Bucket': 'chris-face-images',
                    'Name': i,
                },
            },
        )

imagens = lista_imagens()
nome = "chris-faces"
#criar_colecao(nome)
indexa_colecao(imagens, nome)