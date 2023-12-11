# Examples

```plantuml:md-sample-sequence
@startuml
actor Foo1
boundary Foo2
control Foo3
entity Foo4
database Foo5
collections Foo6
Foo1 -> Foo2 : To boundary
Foo1 -> Foo3 : To control
Foo1 -> Foo4 : To entity
Foo1 -> Foo5 : To database
Foo1 -> Foo6 : To collections
@enduml
```

![](./md-sample-sequence.svg)

```plantuml
!includeurl ./sample-sequence.puml
```

![](./sample-sequence.svg)

```plantuml:sample-sequence
!includeurl ./sample-sequence.puml
```

![](./sample-sequence.svg)
