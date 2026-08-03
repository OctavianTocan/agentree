# Changelog

All notable changes to this project are documented in this file.

This project uses [Release Please](https://github.com/googleapis/release-please)
with [Conventional Commits](https://www.conventionalcommits.org/). Merging the
automated release PR updates this file and publishes a GitHub Release.

## [0.2.0](https://github.com/OctavianTocan/agentree/compare/v0.1.0...v0.2.0) (2026-08-03)


### ⚠ BREAKING CHANGES

* rename project to Agentree

### Features

* Document.load, tree assembly, depth nesting, starts_at_top ([#11](https://github.com/OctavianTocan/agentree/issues/11)) ([557e24f](https://github.com/OctavianTocan/agentree/commit/557e24f9f9d641d75e232aadd746021558080f37))
* emit physical_index as int from structured extraction ([ec9024e](https://github.com/OctavianTocan/agentree/commit/ec9024e7489bb00f4f51743beba56f70b342606b))
* MCP indexing server and tree enrichment ([#20](https://github.com/OctavianTocan/agentree/issues/20)) ([ab641e2](https://github.com/OctavianTocan/agentree/commit/ab641e28ee85bdaff4493e47aa85dbce021bd6e5))


### Bug Fixes

* restore project.dependencies and CodeQL actions permission ([f4f489a](https://github.com/OctavianTocan/agentree/commit/f4f489a8b7a887dcb902361327856712c6510077))


### Documentation

* add Agentree README branding ([#5](https://github.com/OctavianTocan/agentree/issues/5)) ([4975444](https://github.com/OctavianTocan/agentree/commit/497544494477aceafc7e608b093898c95766646d))
* align TODO and README with OutlineSection vocabulary ([07d1979](https://github.com/OctavianTocan/agentree/commit/07d19795ebc2a329252688d6cd3ccd13ace8d1e3))
* fold public-readiness items into the 0.1.0 changelog entry ([75848aa](https://github.com/OctavianTocan/agentree/commit/75848aa2aab8ed045769a8b062499b7eb7d24dec))


### Code Refactoring

* rename project to Agentree ([8fa16c6](https://github.com/OctavianTocan/agentree/commit/8fa16c62b5889a7f83d4da33cb04360cafcbac30))

## [0.1.0](https://github.com/OctavianTocan/agentree/releases/tag/v0.1.0) (2026-07-09)

### Features

- Initial `agentree` package and `agentree` CLI
- Claude Agent SDK and Codex structured-completion adapters
- No-TOC PDF → flat section-structure indexing path
- TOC page detection over leading pages

### Miscellaneous

- Ruff + `ty` + pytest CI via GitHub Actions
- MIT license, PageIndex `NOTICE` / README acknowledgments
- `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS`
- Dependabot (`uv` + GitHub Actions), CodeQL workflow
- Issue and pull request templates
- Sample PDFs under `examples/documents/`
