#version 330
in vec3 aPos;
uniform mediump mat4 uView;
uniform mediump mat4 uProjection;

void main() {
  gl_Position = uProjection * uView * vec4(aPos, 1);
}
