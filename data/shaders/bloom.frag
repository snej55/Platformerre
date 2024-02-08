#version 330 core

uniform sampler2D image;
uniform sampler2D alpha_surf;
uniform sampler2D surf;

uniform float weight[7] = float[] (0.227027, 0.2, 0.17, 0.1216216, 0.08, 0.03, 0.016216);

in vec2 uvs;
out vec4 f_color;

vec4 bitFilter(vec4 color) {
    vec4 bloom_color = color;
    float alpha = (bloom_color.r + bloom_color.g + bloom_color.g) * 0.333;
    if (alpha < 0.95) {
        bloom_color.rgb = vec3(0.0, 0.0, 0.0);
    } 
    return bloom_color;
}

vec4 sampleTex(vec2 coords) {
    return bitFilter(texture(image, coords) + texture(alpha_surf, coords));
}

void main() {
    vec2 tex_offset = 0.5 / textureSize(image, 0) * 0.5;
    vec3 result = bitFilter(texture(image, uvs) + texture(alpha_surf, uvs)).rgb * weight[0];
    for (int i = 1; i < 7; i++) {
        result += sampleTex(uvs + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        result += sampleTex(uvs - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        result += sampleTex(uvs + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
        result += sampleTex(uvs - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
    }
    f_color = vec4(result + texture(surf, uvs).rgb, 1.0);
}