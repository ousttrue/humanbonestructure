#version 330
in vec3 aPos;
in vec4 aColor;
out vec4 vColor;

uniform mediump mat4 uView;
uniform mediump mat4 uProjection;

void main() {
  gl_Position = uProjection * uView * vec4(aPos, 1);
  vColor = aColor;
}
