# OP-9. Contratos LAU y otros

> Manual funcional · Borrador v0.1 · 2026-10-21 · Las marcas **[PREGUNTA On]** se resuelven en la ronda de preguntas y desaparecen de la versión final.

## 9.1 Propósito

Este capítulo explica cómo se gestionan los contratos que quedan fuera del modelo de reservas de coliving: los **arrendamientos de vivienda LAU** de los inquilinos que ya ocupaban los pisos adquiridos por Vandor, y el alquiler de **locales comerciales**, **parkings** y **coworking**. Cubre el alta del contrato, la facturación mensual, la actualización por IPC, los bloqueos de obra al terminar y el seguimiento de la salida del inquilino.

## 9.2 Conceptos

| Concepto | Qué es |
|---|---|
| **Tipo de contrato** | *LAU* (vivienda), *retail* (local), *parking* o *coworking*. Los bloqueos de obra (pre-capex y capex) solo se calculan en los LAU. |
| **Fecha estimada de fin** | Cuándo se prevé que termine el contrato. Sin ella, el contrato es **indefinido** (*long term*). Con fecha de fin, de **duración determinada** (*fixed term*). |
| **Pre-capex / capex** | Periodos de bloqueo del piso tras la salida del inquilino: preparación de la reforma y reforma. Después, el piso pasa a la oferta de coliving. |
| **Situación** | Etiqueta de seguimiento del contrato: en curso, en curso *challenging*, prórroga, pendiente de finalización, litigioso, edad avanzada, finalizado o no aplica. La mantiene el personal y no tiene efecto en el sistema, salvo *edad avanzada*, que la pone el sistema. |
| **Ocupación inconsentida** | El contrato ha vencido y el inquilino sigue ocupando el recurso. No se le emite la factura normal de renta, sino una factura por **indemnización por ocupación**. Se aplica a cualquier tipo de contrato (vivienda, local, parking o coworking). |
| **Edad avanzada** | Inquilino LAU de más de 90 años. Su contrato se trata aparte: no se calculan obras y su fin se mantiene a dos años vista. |
| **Negociación** | Seguimiento de la negociación de salida con el inquilino: aportación recomendada (MAC), lo que pide el inquilino y la propuesta de Vandor. |
| **IPC** | Actualización anual de la renta en el **mes de incremento** del contrato, con un **IPC máximo** si lo hay. |

## 9.3 Tareas

### Dar de alta un contrato

**Qué informar**:

- **Tipo de contrato**, **cliente** (inquilino) y **recurso**; si el contrato incluye más de un recurso (por ejemplo, vivienda y trastero), los **recursos adicionales**.
- **Producto a facturar**: *Renta (LAU) Long term*, *Renta (LAU) Fixed term*, *Local* o *Parquing / Otros*.
- **Fechas**: inicio, fin (si la tiene) y fecha estimada de fin. Si se indica la de fin y no la estimada, el sistema toma la de fin como estimada.
- **Renta** mensual, **medio de pago** (normalmente domiciliación o transferencia), **facturar desde** (si no se factura desde el inicio) y **enviar factura** por email.
- **Otros importes**: deudas anteriores, garantías extra y otros conceptos mensuales.
- **IPC**: si se aplica, el **mes de incremento**, el **IPC máximo** y si se envía el aviso al inquilino.
- **Suministros incluidos**: gas, luz y agua.
- **Fianza depositada**.
- **Calcular bloqueos** (solo LAU), si se quiere que el sistema calcule las obras al terminar.
- Situación, subrogación pendiente, tipo de negocio (en locales) y comentarios. Los documentos del contrato se adjuntan en la pestaña de documentos.

**Qué hace el sistema**:

- **Bloquea el recurso** mientras dure el contrato: hasta la fecha estimada o, si no hay, de forma indefinida. Así no aparece disponible para coliving.
- En los LAU con *Calcular bloqueos* y fecha estimada, calcula y bloquea:
  - **Pre-capex**: hasta el último día del mes, dos meses después de la fecha estimada.
  - **Capex**: hasta el último día del mes, cuatro meses después del fin del pre-capex.

  Las fechas se pueden cambiar a mano en el contrato; los bloqueos se recalculan al guardarlo.
- Los bloqueos de un contrato **solo se cambian desde el propio contrato**: no se pueden editar ni borrar en la ficha del recurso.

### Facturar la renta mensual

**Qué hace el sistema**: cada mes, para los contratos vigentes con renta que aún no tienen factura ese mes (y a partir de *facturar desde*):

- Emite una **factura del propietario** en la **serie LAU** con la renta, los otros importes y los servicios adicionales pendientes del contrato.
- Crea el **cobro** por el terminal de **Vandor**, con el medio de pago del contrato.
- Si se ha marcado **enviar factura**, la envía por email desde Vandor.

**Ocupación inconsentida**: si el contrato está marcado como *ocupación inconsentida*, solo se factura si además se marca **facturar inconsentida**, y el concepto es *Indemnización por ocupación inconsentida* en lugar de *Renta mensual*.

**Domiciliaciones**: los cobros domiciliados de Vandor salen en la hoja *Vandor* del informe SEPA (ver *Facturación y cobros*).

### Actualizar la renta por IPC

**Qué hacer**: mantener el **IPC** en *Auxiliares › IPC*: cada mes, el último valor publicado con su fecha.

**Qué hace el sistema** (proceso mensual, el día 28):

1. **Dos meses antes** del mes de incremento de cada contrato con IPC: fija el IPC a aplicar (el último registrado, con el máximo del contrato si lo tiene) y, si el contrato lo indica, envía al inquilino el email **ipc** desde Vandor, con copia a Vandor.
2. **Un mes antes** del mes de incremento: actualiza la renta (renta × (1 + IPC aplicado)) y guarda la anterior.

Solo se actualizan los contratos con IPC activo y vigentes (fecha estimada futura o sin fecha), una vez al año.

**Comprobar**: que el IPC del mes está registrado antes del día 28. El dashboard LAU y el contrato muestran el IPC aplicado, la renta anterior y las fechas de la última notificación y del último incremento.

### Seguir el fin de un contrato

El **dashboard LAU** reúne el seguimiento de los contratos que terminan:

| Qué | Qué registrar |
|---|---|
| **Fin de contrato** | Fecha del **burofax** de fin de contrato y aviso al inquilino un mes antes. |
| **Negociación** de la salida | Estado (no iniciada, en curso, fallida, sin opción, aceptada), aportación recomendada (MAC), petición del inquilino, propuesta de Vandor y su fecha. |
| **Indemnización** | Importe, fecha prevista y fecha efectiva de pago. |
| **ITP** | Fecha prevista (un mes después de la indemnización, la calcula el sistema) y fecha efectiva de pago. |
| **Fianza** | Importe a devolver, fecha prevista, importe devuelto y fecha efectiva. |

La **aportación recomendada (MAC)** sale del porcentaje de contribución sobre la diferencia entre el valor del piso vacío y el valor con el inquilino (valoraciones pre-capex del recurso). Si se informa el importe, el sistema calcula el porcentaje, y al revés.

**Al terminar el contrato**: informar la **fecha de fin** real, ajustar la **fecha estimada de fin** a esa misma fecha y poner la situación *finalizado*. Los bloqueos se recalculan a partir de la fecha estimada: el del contrato hasta ella y, si procede, los de obra a continuación. Si solo se cambia la fecha de fin, el bloqueo sigue llegando a la estimada anterior.

### Inquilinos de edad avanzada

**Qué hace el sistema** (proceso mensual, el día 1): los inquilinos LAU de más de 90 años con contrato vigente pasan a la situación **edad avanzada**; su fecha estimada de fin se mantiene siempre a dos años vista (fin de mes) y se quitan las fechas de pre-capex y capex. Así, el piso no aparece como disponible próximamente ni se planifican obras.

### Rentas máximas de la Ley de vivienda

La última renta de un contrato LAU y su fecha de fin se usan para calcular la **renta máxima** del piso durante 5 años en Barcelona y Bilbao. El cálculo no las toma del contrato, sino de la **ficha del piso**: al terminar un contrato LAU hay que cargarlas en el piso con la carga Excel **Recursos** (fecha fin y renta del último LAU). Ver *Inventario y precios*, régimen de renta.

## 9.4 Automático y manual

| Qué | A / M |
|---|---|
| Alta y mantenimiento del contrato | M |
| Bloqueos del contrato, pre-capex y capex | A |
| Facturación mensual, cobro y envío de la factura | A |
| Registro mensual del IPC | M |
| Aviso de IPC y actualización de la renta | A |
| Paso a *edad avanzada* y fin a dos años vista | A |
| Fin de contrato, negociación, indemnización, ITP y fianza | M |
| Datos del último LAU en el piso (carga Excel *Recursos*) | M |
| Cobros domiciliados (remesa) | M (informe SEPA) |

## 9.5 Excepciones

| Situación | Qué pasa | Qué hacer |
|---|---|---|
| Error "No se pueden modificar bloqueos de reservas LAU" | Se ha intentado cambiar o borrar en el recurso un bloqueo de un contrato. | Cambiar las fechas en el contrato. |
| Error "La fecha fin de pre-capex (o capex) es incorrecta" | La fecha es anterior a la que le precede. | Corregir las fechas en el contrato. |
| No se ha actualizado una renta por IPC | El IPC no tiene *Aplicar IPC*, el mes de incremento no es el esperado, el contrato ya no está vigente o no había IPC registrado. | Revisar el contrato y el IPC; actualizar la renta a mano si hace falta. |
| Un inquilino en ocupación inconsentida no recibe factura | Falta marcar *facturar inconsentida*. | Marcarlo si procede. |

## 9.6 Fuentes

| Tema | Dónde está |
|---|---|
| Validación, fechas de obra, ITP y aportación | Reglas de la base de datos de los contratos LAU y otros |
| Bloqueos | Reglas de la base de datos de los contratos LAU y otros |
| IPC y edad avanzada | Procesos programados de la base de datos (mensuales) |
| Facturación | Proceso automático de facturación |
| Dashboard LAU | Backoffice complementario |

## 9.7 Pendiente de confirmar

| Tema | Quién o qué lo confirma |
|---|---|
| — | — |
