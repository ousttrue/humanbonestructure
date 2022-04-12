#version 330
in vec3 aPos;
in vec3 aNormal;
in vec2 aUV;
in vec4 aBoneIndex;
in vec4 aBoneWeight;

out vec3 vUVL;
uniform mediump mat4 uModel;
uniform mediump mat4 uView;
uniform mediump mat4 uProjection;
uniform mat4 uBoneMatrices[250];

void main() {

  vec4 position = vec4(0, 0, 0, 0);
  vec4 normal = vec4(0, 0, 0, 0);
  if (aBoneWeight.x > 0) {
    int index = int(aBoneIndex.x);
    position += (uBoneMatrices[index] * vec4(aPos, 1)) * aBoneWeight.x;
    normal += (uBoneMatrices[index] * vec4(aNormal, 0)) * aBoneWeight.x;
  }
  if (aBoneWeight.y > 0) {
    int index = int(aBoneIndex.y);
    position += (uBoneMatrices[index] * vec4(aPos, 1)) * aBoneWeight.y;
    normal += (uBoneMatrices[index] * vec4(aNormal, 0)) * aBoneWeight.y;
  }
  if (aBoneWeight.z > 0) {
    int index = int(aBoneIndex.z);
    position += (uBoneMatrices[index] * vec4(aPos, 1)) * aBoneWeight.z;
    normal += (uBoneMatrices[index] * vec4(aNormal, 0)) * aBoneWeight.z;
  }
  if (aBoneWeight.w > 0) {
    int index = int(aBoneIndex.w);
    position += (uBoneMatrices[index] * vec4(aPos, 1)) * aBoneWeight.w;
    normal += (uBoneMatrices[index] * vec4(aNormal, 0)) * aBoneWeight.w;
  }

  gl_Position = uProjection * uView * uModel * position;

  // lambert
  vec3 L = normalize(vec3(-1, -2, 3));
  vec3 N = normalize(normal.xyz);
  float v = max(dot(N, L), 0.2);
  vUVL = vec3(aUV, v);
}
