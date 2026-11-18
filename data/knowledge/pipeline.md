# Carga incremental

A carga incremental usa o identificador do pedido e a versão positiva de cada registro. Uma versão mais recente substitui o pedido. Versões iguais ou anteriores preservam o registro existente.

Cada lote valida cliente, data, centavos e duplicidades. Linhas inválidas são rejeitadas com motivo. As linhas válidas são gravadas em uma transação com o histórico de execução.
