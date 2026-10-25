# farmai-testes-status

Status público e mínimo dos testes automatizados do MVP FarmAI.

- `status/ultimo.json`: atualizado pelo GitHub Actions do repositório privado a cada rodada de testes. Contém apenas códigos de critério (`H10-CA02`), ids de casos de referência (`GD-AUD-01`) e o resultado de cada um (passou, falhou, pulado, pendente).
- `sincroniza-painel.py`: script que junta esse status com as histórias do Painel de histórias e calcula os indicadores "x/y CTs passed".

Este repositório **não** contém código-fonte, títulos de testes, mensagens de erro, endereços de ambientes, credenciais nem dados de pessoas. O código e as evidências completas ficam no repositório privado.
