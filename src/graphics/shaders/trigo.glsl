
vec2 rotate_z(in vec2 v, in float t) {
    return vec2(
        cos(t) * v.x - sin(t) * v.y,
        sin(t) * v.x + cos(t) * v.y
    );
}
