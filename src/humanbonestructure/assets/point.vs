#version 330
in vec2 aPos;
in vec3 aCol;
out vec3 vCol;
void main() {
  gl_Position = vec4(aPos, 0.0, 1.0);
  vCol = aCol;
}
