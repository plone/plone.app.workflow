Fire ``PrincipalLocalRolesModifiedEvent`` for each user or group whose local roles the sharing view changes, with the roles before and after, and ``LocalRolesInheritanceModifiedEvent`` when it switches inheriting local roles on or off.
Audit logging needs these to record privilege changes, as required by the NIS2 directive.
[jladage]
