-- Create user for testing read-only connections (DATABASE_URL=postgres://ons_alpha_read_only@db/ons_alpha)
CREATE ROLE ons_alpha_read_only WITH LOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public to ons_alpha_read_only;
GRANT INSERT, UPDATE ON wagtailimages_rendition, wagtailforms_formsubmission TO ons_alpha_read_only;
