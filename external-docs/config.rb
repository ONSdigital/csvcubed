require 'govuk_tech_docs'

GovukTechDocs.configure(self)

configure :build do
    set :http_prefix, (ENV["HTTP_PREFIX"] || Dir.pwd)
end

