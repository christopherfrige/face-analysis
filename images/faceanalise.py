import boto3
import json

# Inicializa os serviços da s3 (armazenar), e o rekognition (identificar)
s3 = boto3.resource('s3')
client = boto3.client('rekognition')

# Indexa a imagem ser analisada, e retorna os detalhes de cada rosto presente nela
def detectaFaces():
    faces_detectadas=client.index_faces(
        CollectionId='chris-faces',
        DetectionAttributes=['DEFAULT'],
        ExternalImageId='temp', #temporária
        Image={
            'S3Object': {
                'Bucket': 'chris-face-images',
                'Name':'imagens/analise.png',
            },
         },
    )
    return faces_detectadas

def criarListaFaceIdDetectadas(faces_detectadas):
    faceId_detectadas = []
    for imagens in range(len(faces_detectadas['FaceRecords'])):
        # Pega a faceId no json gerado pela imagem e coloca numa lista
        faceId_detectadas.append(faces_detectadas['FaceRecords'][imagens]['Face']['FaceId'])
    return faceId_detectadas


def compararFaces(faceId_detectadas):
    resultado_comparacao = []
    for codigoFace in faceId_detectadas:
        resultado_comparacao.append(
            # Procura na coleção cada uma das faces da imagem a ser analisada
            client.search_faces(
                CollectionId='chris-faces',
                FaceId=codigoFace,
            )
        )
    return resultado_comparacao


def gera_dados_json(resultado_comparacao):
    dados_json = []
    for face_match in resultado_comparacao:
        if len(face_match.get('FaceMatches'))>=1:
            perfil = dict(
                nome = face_match['FaceMatches'][0]['Face']['ExternalImageId'],
                similaridade = round(face_match['FaceMatches'][0]['Similarity'], 2), # 2 casas decimais          
            )
            dados_json.append(perfil)
    return dados_json


def publicarDados(dados_json):
    arquivo = s3.Object('chris-face-site', 'dados.json')
    arquivo.put(Body=json.dumps(dados_json))

# Limpar as imagens temporárias que estão na coleção
def excluirImagemColecao(faceId_detectadas):
    client.delete_faces(
        CollectionId='chris-faces',
        FaceIds=faceId_detectadas
    )


def main(event, context):
    faces_detectadas = detectaFaces()
    faceId_detectadas = criarListaFaceIdDetectadas(faces_detectadas)
    resultado_comparacao = compararFaces(faceId_detectadas)
    dados_json = gera_dados_json(resultado_comparacao)
    publicarDados(dados_json)
    excluirImagemColecao(faceId_detectadas)

    print(json.dumps(dados_json, indent=4))