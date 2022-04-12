#version 330
in vec3 vUVL;
out vec4 FragColor;
void main() {
  float v = vUVL.z;
  FragColor = vec4(v, v, v, 1.0);
}
