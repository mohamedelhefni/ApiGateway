
package envoy.http.roles

import future.keywords.if
import future.keywords.in

default allow := false

# Sets are collections of values. To test if a value `x` is a member of `set`
# you can write `set[x]`, or `x in set`. In this case we check if the `"username"`
# claim is contained in the `admin_users` set.
allow if claims.username in admin_users

# admin_users is a set of usernames.
admin_users := {
	"hefni",
	"mohamed",
}

# See the 'JWT Decoding' example for an explanation.
claims := payload if {
	v := input.token

	startswith(v, "Bearer ")
	t := substring(v, count("Bearer "), -1)
	io.jwt.verify_hs256(t, "hefni-key")
	[_, payload, _] := io.jwt.decode(t)
}

