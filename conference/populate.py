# -*- coding: utf-8 -*-

# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

from django.contrib.auth.models import User

admin = User(username='boostcon', is_staff=True, is_active=True, is_superuser=True)
admin.set_password('crtplib')
admin.save()

from models import *

class Saver(object):
    def __ror__(self, inst):
        inst.save()
        return inst

save = Saver()

#
# Conference
#
boostcon07 = Conference(name='boostcon',
                        start=date(2007,5,13),
                        finish=date(2007,5,18)) | save

#
# TimeBlock
#
mon = [
    TimeBlock(start=datetime(2007,5,14,*t), conference=boostcon07)

    for t in ((9,00), (11,00), (12+2,30), (12+4,30))]

for block in mon:
    block.save()

    for i,name in enumerate(('tue','wed','thu','fri')):
        copy = TimeBlock(start=block.start+timedelta(i+1),conference=block.conference)
        copy.save()
        locals()[name] = locals().get(name,[]) + [copy]

fri[2].delete()
fri[3].delete()

#
# Track
#
user = Track(name='Track I',description='was the user track',conference=boostcon07) | save

dev = Track(name='Track II',description='was the developer track',conference=boostcon07) | save

#
# Presenter
#
abrahams = Presenter(
  first_name = "Dave",
  last_name = "Abrahams",
  email = "dave@boost_consulting.com",
  bio = u"""
Dave Abrahams is a founding member of boost.org_ and an active
participant in the ANSI/ISO C++ standardization committee.  He
has been a software professional since 1987, his a broad range of
experience in industry including shrink-wrap software
development, embedded systems design and natural language
processing.  He has authored eight Boost libraries and has made
contributions to numerous others.

.. _boost.org: http://www.boost.org

Dave made his mark on C++ standardization by developing a
conceptual framework for understanding exception-safety and
applying it to the C++ standard library.  Dave created the first
exception-safe standard library implementation and, with Greg
Colvin, drafted the proposals that eventually became the standard
library's exception-safety guarantees.

In 2001 he founded Boost Consulting to deliver on the promise of
advanced, open-source C++ libraries, and has been happily
developing C++ libraries, teaching about C++ and Boost, and
nurturing the Boost community ever since.
""") | save

de_guzman = Presenter(
    first_name = 'Joel',
    last_name = 'de Guzman',
    email = 'joel@boost-consulting.com',
    bio = u"""
Joel de Guzman is the author of the Boost Spirit Parser Library, the
Boost Fusion Library and the Phoenix Functional-C++ library. He is a
highly experienced software architect and engineer with over 18 years of
professional experience, with specialization and expertise in generic
C++ cross platform libraries and frameworks. Joel is a consultant at
Boost Consulting since 2002 and has provided support and development
services focused on the Boost libraries. His interests include Parser
Generators, Scripting language interpreters and compilers, Domain
Specific Embedded Languages, 2D graphics and GUI frameworks.
""") | save
    
garland = Presenter(
  first_name = 'Jeff',
  last_name = 'Garland',
  email = 'jeff@crystalclearsoftware.com',
  bio = u"""
Jeff Garland has worked on many large-scale, distributed software projects 
over the past 20+ years.  The systems span many different domains including 
telephone switching, industrial process control, satellite ground control, 
ip-based communications, and financial systems.  He has written C++ networked 
code for several large systems including the development high performance 
network servers and data distribution frameworks.

Mr. Garland's interest in Boost started in 2000 as a user.  Since then he has 
developed Boost.date_time, become a moderator, served as a review manager for 
several libraries (including asio and serialization), administered the Boost 
wiki, and served as a mentor for Google Summer of Code.  Mr. Garland holds a 
Master's degree in Computer Science from Arizona State University and a 
Bachelor of Science in Systems Engineering from the University of Arizona. He 
is co-author of Large Scale Software Architecture: A Practical Guide Using 
UML.  He is currently Principal Consultant for his own company: CrystalClear 
Software, Inc.
""") | save

gregor = Presenter(
    bio=u"""
Doug is a long-time Boost moderator and developer. He has
authored several Boost libraries, including Function (part of the
first C++ library extensions technical report), Signals, and MPI. As a
member of the ISO C++ standards committee, Doug is active in both the
library and evolution working groups and is leading the effort specify
and implement concepts for C++0x. Doug is a post-doctoral researcher
in the Open Systems Laboratory at Indiana University.
""",
    
    first_name='Douglas',
    last_name='Gregor',
    email='dgregor@osl.iu.edu'
) | save

marcus = Presenter(
    bio=u"""
Mat Marcus is a senior computer scientist in the Software Technology Lab at Adobe Systems,
Inc. He has been developing software since 1985. Recent projects include a collaboration with 
Alex Stepanov on a programming class and work on the Adobe Source Library. Mat's first
contribution to Boost came in the summer of 2000, when he discovered a way to exploit the
properties of the sizeof operator to simulate partial specialization (is_pointer, etc. with
Jesse Jones). Mat lives in Seattle with his wife and son.
""",
    first_name = 'Mat',
    last_name = 'Marcus',
    email='mmarcus@adobe.com'
) | save

meyers = Presenter(
  first_name='Scott',
  last_name='Meyers',
  email = 'smeyers@aristeia.com',
  bio = u"""
Scott Meyers is one of the world's foremost authorities on C++;
he provides training and consulting services to clients
worldwide.  He wrote the best-selling Effective C++ series
(Effective C++, More Effective C++, and Effective STL), designed
the innovative Effective C++ CD, is Consulting Editor for Addison
Wesley's Effective Software Development Series, and serves on the
Advisory Board for The C++ Source
(http://www.artima.com/cppsource).  He has a Ph.D in Computer
Science from Brown University.  His web site is aristeia.com.
""") | save

niebler = Presenter(
  first_name='Eric',
  last_name='Niebler',
  email='eric@boost-consulting.com',
  bio=u"""
Eric Niebler has been a professional C++ developer for over 10 years. He 
has helped develop natural language processing software for Microsoft 
Research and template libraries for Visual C++. Since 2003, Eric has 
worked as a Boost consultant with David Abrahams. He is especially 
interested in text processing, pattern matching and the design of 
domain-specific embedded libraries. Eric authored the popular GRETA 
regular expression template library in addition to the Boost libraries 
Foreach and Xpressive. He also has assisted in the development of 
several other Boost libraries and has two more Boost libraries awaiting 
review. Eric has written articles for the C/C++ Users' Journal, MSDN 
Magazine and The C++ Source, and spoken about C++ at OOPSLA/LCSD and C++ 
Connections.
""") | save


henney = Presenter(
    first_name='Kevlin',
    last_name='Henney',
    email='kevlin@curbralan.com',
    
    bio=u"""
Kevlin Henney is an independent consultant and trainer based in the UK.
He specialises in programming languages and techniques, patterns and
software architecture, and agile development, with a particular emphasis
on bringing these often separated worlds together.

He has been a columnist and contributor for various magazines, including
Application Development Advisor, C++ Report, and C/C++ Users Journal
online. He is currently a columnist for The Register's Reg Developer.
Kevlin is coauthor of two forthcoming volumes in the Pattern-Oriented
Software Architecture series. He is a long-time member of the ACCU and a
past contributor to Boost. For better or for worse, he has found himself
drawn into various committees, including the one for the C++ standard,
the one for The C++ Source, and the one for this conference.
""") | save

hinnant = Presenter(
    bio=u"""
Currently employed with Apple as a software engineer. Previously with
Metrowerks/Motorola/Freescale and author of the CodeWarrior C++ standard
library.  C++ committee member currently serving as Library Working Group
Chairman. Co-author/co-inventor and head cheerleader of the rvalue reference
proposal for C++0X.
""",

    first_name='Howard',
    last_name='Hinnant',
    email='howard.hinnant@gmail.com') | save

kaiser = Presenter(
  first_name='Hartmut',
  last_name='Kaiser',
  email='HartmutKaiser@t-online.de',
  bio=u"""
After 15+ interesting years that Hartmut spent working in industrial
software development, he still tremendously enjoys working with modern
software development technologies and techniques. His preferred field of
interest is the software development in the area of object-oriented and
component-based programming in C++ and its application in complex contexts,
such as grid and distributed computing, spatial information systems,
internet based applications, and parser technologies. He enjoys using and
learning about modern C++ programming techniques, such as template based
generic and meta-programming and preprocessor based meta-programming.
""") | save

parent = Presenter(
    first_name='Sean',
    last_name='Parent',
    email='sparent@adobe.com',
    
    bio=u"""
Sean Parent is a principal scientist at Adobe Systems and engineering manager of
the Adobe Software Technology Lab. One of his team's current projects is the
Adobe Source Libraries <http://opensource.adobe.com/>, including two libraries
for declarative user interface logic and layout. Sean has been at Adobe since
1993 when he joined as a senior engineer working on Photoshop. From 1988 through
1993 Sean worked at Apple where he was part of the system software team that
developed the technologies allowing Apple's successful transition to the PowerPC
RISC processor. Sean holds a number of software patents and is a graduate of
Seattle University.
""") | save

siek = Presenter(
    bio=u"""
Jeremy is a professor at the University of Colorado at Boulder and
a research scientist at LogicBlox inc. Jeremy is the author of several Boost
libraries, including the Graph, Iterator Adaptor, Dynamic Bitset, and Concept
Check libraries. Jeremy is a long time advocate and practitioner of generic programming.
His Ph.D. thesis laid the foundation for the “concepts” feature for C++0X
that will greatly improve the language's support for generic programming.""",
    first_name='Jeremy',
    last_name='Siek',
    email='jeremy.siek@colorado.edu') | save

shead = Presenter(
    bio= u"""
Timothy M. Shead is an application-level software engineer at
Sandia National Laboratories with an extensive background in
C++, 3D graphics, and animation.
""",

    first_name='Timothy',
    last_name='Shead',
    email='tshead@sandia.gov'
    ) | save

#
# Sessions
#
beginner = Session.beginner
intermediate = Session.intermediate
advanced = Session.advanced

shotgun = Session(
    title="A Shotgun Firehose Introduction to TR1 and Boost", 
    short_title="Firehose Intro", 
    presenter=meyers,
    track=user,
    start=mon[0],
    duration=4*90,
    description=u"""
TR1 is a specification for 14 new kinds of standard library
functionality, 13 of which are already part of the draft version
of C++0x and most of which were based on Boost libraries.  Boost
also offers dozens of libraries offering functionality not in
TR1.  This tutorial discusses a semi-random collection of
libraries in TR1 and Boost (that's the shotgun part), giving an
overview of the functionality each offers.  It covers a *lot* of
information in the time available (that's the firehose part), and
it tries to include insights difficult or impossible to glean
from the usual library documentation.

From TR1, we'll discuss smart pointers (shared_ptr and weak_ptr), unordered
containers (hash tables), regular expressions, generalized function pointers and
binders, tuples, and fixed-size arrays. From Boost, we'll cover non-TR1 smart
pointers, static asserts, lambda, file system, conversions, format, and variant.
For a detailed topic outline, consult `the description at Scott's web site`__.

__ http://www.aristeia.com/TR1andBoost_frames.html
""") | save

meta = Session(
    title="Boost Metaprogramming Concepts and Frameworks", 
    short_title="Metaprogramming", 
    presenter=abrahams,
    track=dev,
    start=mon[2],
    duration=2*90,
    description=u"""
Have you ever wondered what makes the difference between "spaghetti
code" and pure poetry?  It's abstraction.  Many of the worst code
integrity problems stem from programming at a level of abstraction
far below that of our mental model.  Boost libraries use
metaprogramming to provide interfaces that directly reflect the
programmer's domain model and notation, all without loss of
efficiency.

This session explores both "big picture" ideas and practical tools.
We'll discuss what metaprogramming is, why it matters, and show how
the unique combination of features in C++ make it an especially
powerful language for metaprogramming.  We'll also get a taste of
high-level metaprogramming abstractions by using several Boost
metaprogramming libraries—MPL, Preprocessor, and the Fusion
tuple library—to solve real problems.

This course is based on "C++ Template Metaprogramming: Concepts,
Tools and Techniques from Boost and Beyond,"
(http://www.boost-consulting.com/mplbook), although familiarity
with the book is not a prerequisite.  For those who have read it,
some new material will also be covered.
""",
    level=advanced,
    attendee_background=u'Mostly people who write libraries and code that will be reused.'
    ) | save

network = Session(
    title="Network Programming with Boost", 
    short_title="Network Programming", 
    presenter=garland,
    start=wed[0],
    track=user,
    duration=4*90,
    description=u"""
This tutorial will provide an introduction to network programming with 
Boost.  With the adoption of the Asio library, Boost finally has a library 
that provides networking capabilities.  This tutorial will provide a basic 
introduction to using Asio to write network enabled programs.

Starting with a simple synchronous, iostream-based example to retrieve a web 
page the tutorial first introduces basic network programming concepts such as 
clients, servers, endpoints, and buffers. After looking at a synchronous 
version, the web page retrieval program is converted to use asynchronous i/o 
introducing multiplexing and handler-based programming.

In the next section, the a distributed “hello world” client and server is 
developed introducing additional networking concepts such as acceptors, 
connectors, and timers.  This example is then extending using 
Boost.Serialization to exchange message objects between peer processes.

The tutorial concludes with a survey of other related topics including the 
relationship of Asio and Boost.threads, encrypted socket handling using Secure 
Sockets, and connection-less protocols (UDP).

There will be at least 2 hands-on exercises to help students get started with 
network programming.

Exercise 1: Students will re-write sync client as an async program.

Exercise 2: Students will write a basic server using async handling.

Tutorial Objectives
- Provide students with the basics of writing networked programs

- Provide an understanding of using Asio to write network enabled programs including:
  - an understanding of 'asynchronous programming'
  - basics of TCP based sockets
  - integration of sockets and i/o streams
  - understanding of using timers in network programming

- Using serialization with Asio to build a general object messaging frameworks
""",
    level=beginner|intermediate,
    attendee_background=u'Attendees should have a basic background in C++.',
    boost_components='Asio, Serialization, Regex, Bind, Date-Time',
    format='lecture'
) | save

text = Session(
  title="Text Processing with Boost", 
  short_title="Text Processing", 
  presenter=niebler,
  start=tue[0],
  duration=90*2,
  format='tutorial',
  track=dev,
  level=beginner,
  description=u"""
The abysmal support in the C and C++ standard libraries for string 
handling has driven many programmers to other languages like Perl and 
Python. Boost aims to reverse that trend. Libraries such as 
Boost.Lexical_cast, Boost.String_algo, Boost.Regex, Boost.Xpressive and 
Boost.Spirit are invaluable tools for slicing and dicing strings. If 
your task is as simple as turning an integer into a string, or as 
complicated as developing a parser generator for a new scripting 
language, Boost has a library that can help. In addition to covering all 
the afore mentioned libraries from a user's perspective, we'll also look 
at how Boost can be used to get more out of the standard IOstreams, and 
discover some hidden gems in Boost for dealing with Unicode.
""") | save

spirit2 = Session(
    title="A cookbook approach to parsing and output generation with Spirit2", 
    short_title="Spirit2", 
    presenters=(kaiser,de_guzman),
    start=thu[1],
    track=dev,
    description=u"""
Spirit2 will debut on the Boost conference. It shall be a complete parsing and 
output generation system with a symmetrical architecture that attempts to cover 
the whole spectrum from lexing to output generation. Spirit2 uses a EBNF oriented 
syntax to describe a grammar (for parsing) and a output format (for generation) 
directly in C++. This allows to construct programs able to parse input token 
sequences conforming to this grammar and to generate output token sequences
Conforming to the output format. The system is modular, and consists of four 
independent subsystems:

+-----------------------------------------+-----------------------------------------+
| Parsing                                 | Generation                              |
+--------------------+--------------------+--------------------+--------------------+
| Lexer ➡            | Parser ➡           | Deparser ➡         | Delexer            |
+--------------------+--------------------+--------------------+--------------------+

We propose a half day talk divided into two parts:

1) A cookbook approach to parsing and output generation with Spirit2
2) Inside Spirit2

The target audience for the first part shall be intermediate C++ programmers 
with basic background on parsing. The second part shall target intermediate to 
advanced C++ programmers, prefereably with basic template metaprogramming 
knowledge and the Boost libraries (especially MPL).

For the first part, we shall cover a lot of ground through examples; lots of 
them. We shall present them in a cookbook style approach. The workshop will give 
a thorough introduction to Spirit's subsystems, their features, how to use them, 
how to extend them for special needs. We shall present real world examples from 
the simplest comma-separated-list parsing, to simple calculator examples, to the 
more complex scripting languages. We shall cover semantic processing and backend 
generation to complete the picture. We shall show how combining the various 
subsystems work for language transformations. We will have examples on 
generating code for a virtual machine, generation of HTML and XML, and building 
a dynamic GUI layout, to highlight a few. We shall provide step by step 
tutorials on hand coded semantic actions, automatic abstract syntax tree 
generation, and the deparser/delexer subsystems. 

For the second part, "Inside Spirit", we shall provide a walk-through of the 
infrastructure of Spirit2, the tools it uses (MPL, Fusion, Proto and 
Lambda/Phoenix). We shall show how these libraries are instrumental in the 
development of Spirit2. We shall show how Spirit actually necessitated and 
influenced the development of some of these libraries. We will cover design 
problems related to DSEL's. We shall show how to use a common code base to 
handle the compile time construction of parsers and generators, using Proto- a 
DSEL framework. We will provide insights on related implementation details, and 
performance comparisons.
""") | save

hybrid = Session(
    title="Hybrid Development with Boost.Python (and More!)",
    short_title="Hybrid", 
    presenter=abrahams,
    format='tutorial',
    start=tue[2],
    track=dev,
    description=u"""
Python and C++ are in many ways as different as two languages could
be: while C++ is usually compiled to machine-code, Python is
interpreted. Python's dynamic type system is often cited as the
foundation of its flexibility, while in C++ static typing is the
cornerstone of its efficiency. C++ has an intricate and difficult
compile-time meta-language, while in Python, practically everything
happens at runtime.

Yet for many programmers, these very differences mean that Python
and C++ complement one another perfectly. Performance bottlenecks
in Python programs can be rewritten in C++ for maximal speed, and
authors of powerful C++ libraries choose Python as a middleware
language for its flexible system integration
capabilities.

Boost.Python is a C++ library that provides a concise IDL-like
interface for binding C++ classes and functions to Python.
Leveraging the full power of C++ compile-time introspection, and of
recently developed metaprogramming techniques, this integration is
achieved entirely in pure C++, without introducing a new
syntax. Boost.Python's rich set of features and high-level
interface make it possible to engineer packages from the ground up
as hybrid systems, giving programmers easy and coherent access to
both the efficient compile-time polymorphism of C++ and the
extremely convenient run-time polymorphism of Python.

In this tutorial, we describe the models for integrating C++ and
Python, show how Boost.Python improves on the facilities provided
by Python's 'C' API, and walk through the key concepts of the
Boost.Python library.  We'll briefly discuss the Py++
code-generating front-end, which parses C++ header files and
generates Boost.Python binding code.  Finally, we'll spend a little
time discussing the Boost.Langbinding concept, an architecture that
would integrate the functionality of Boost.Python and its many
imitators that target other dynamic languages, using pluggable
backends for each supported dynamic language.
        """) | save
        
future = Session(
    title="A Possible Future for Software Development", 
    short_title="Future", 
    presenter=parent,
    start=TimeBlock(start=datetime(2007,5,16,12+7,30), duration=120, conference=boostcon07) | save,
    format='keynote',
    description=u"""
This talk begins with an overview of software development at Adobe
and a look at industry trends towards systems built around object
oriented frameworks; why they "work", and why they ultimately fail
to deliver quality, scalable, software. We'll look at a possible
alternative to this future, combining generic programming with
declarative programming to build high quality, scalable systems.

I'll demonstrate how these ideas manifest in Boost and the standard
library and how they are being combined and explored in the Adobe
Source Libraries.
""") | save
        
agile = Session(
    title="Hands-on Agile Development Workshop with Boost", 
    short_title="Agile",
    start=thu[0],
    duration=90*4,
    presenter=henney,
    format='workshop',
    description=u"""
Agile development processes are intended to help developers avoid the
problems of analysis paralysis, big up-front design, rushed testing and
changing requirements. They treat analysis and design as continuous
activities that start early in development but continue throughout,
rather than as segregated phases divorced from other development
activities.

Development is dynamically planned as incremental and iterative. Coding
and testing are considered together and from an early stage in
development. In particular, incremental design, continuous testing and
responsive refactoring make up the programmer-facing discipline of
Test-Driven Development (TDD). The goal of this workshop is twofold: (1)
it aims to offer attendees hands-on experience of many of the practices
involved in the construction phase of a development lifecycle and (2) it
introduces some of the common Boost libraries to raise development above
the level of standard C++ libraries.

As its title suggests, this workshop actually is a workshop! Attendees
will learn about the development side of agile development by doing it
and some common Boost libraries by using them. The workshop is based on
undertaking four rapid sprints of development, working on a clearly
bounded and well-defined problem. The technical emphasis is on the role
of libraries in promoting responsive and streamlined development, with
Boost as a leading concrete example. The process emphasis is on scope
management, iteration planning, TDD, pair programming and other
practices and principles drawn from agile approaches such as Extreme
Programming, Scrum and Lean Software Development, with guidance and
feedback both during and in between iterations.
""",
    track=user,
    level=beginner|intermediate
    ) | save

rvalue = Session(
    title="An Introduction to the Rvalue Reference in C++0X", 
    short_title="Rvalue Reference",
    duration=2*90,
    presenter=hinnant,
    start=wed[2],
    track=dev,
    format='tutorial',
    description=u"""
Rvalue reference is tiny addition to the C++ language which will have a
large impact on the way you design your C++ classes and algorithms.  It
will free youto use standard library components in a much more flexible
manner, and without having to worry about the cost of copying huge objects
around.

Have you ever passed a large container by reference to a function as an
"outputparameter" when what you really wanted to do was have the function
return the container by value?  Sure, who hasn't.  This session will teach
you how and why C++0X will make it guaranteed-efficient to return standard
containers by value from functions.  Learn how to adapt your own heavy weight
classes so that they too can always be returned from functions efficiently.

Have you ever put a non-copyable type on the heap, just for the purpose of
being able to pass it among different scopes?  Perhaps you wanted to pass it
into a function, return it from a function, or put it into a container.  Such
practice is now a thing of the past.  As an example, the standard
(non-copyable) stream types are now movable.  They can be put directly
into containers, and returned from functions.  This tutorial will explain
how that is now possible so that you can do the same with your own
non-copyable types.

Have you ever wanted to put auto_ptr into a vector, but had to compromise
by using shared_ptr instead?  This tutorial introduces unique_ptr, which
in a nutshell is an "auto_ptr that works".  It has the same overhead and
semantics as auto_ptr, but is safe to put into containers.

Have you ever needed to forward a generic argument, either lvalue or rvalue,
without changing its cv-qualification?  Or equivalently, have you ever been
frustrated that you can't pass rvalue (temporary) arguments to boost::bind
functionals?  No longer.

All of this and more simply represent applications of the rvalue reference. 
Learn the few simple characteristics of the rvalue reference and you will
see how all of the above is now possible, not only for the standard library,
but for your own code as well.  Get a head start on C++0X.  By doing so you
may well find your own innovative uses of this new tool.
    """) | save

con_intro = Session(
    title="An Introduction to Concepts in C++0x", 
    short_title="Concepts Intro", 
    presenter=gregor,
    start=wed[0],
    track=dev,
    duration=2*90,
    format='tutorial',
    description=u"""
Concepts are a major addition to C++0x that make templates more
robust, more powerful, and easier to write and use. At their most
basic level, concepts provide a type system for templates.  Using
concepts, the C++ compiler is able to detect errors in the definition
and use of templates before they are instantiated.  One immediately
obvious benefit of this separate type-checking capability is a
dramatic improvement in error messages resulting from improper use of
templates. Look a little deeper and we find that concepts support an
entirely new programming paradigm, Generic Programming, enabling the
construction of a new breed of generic libraries that provide better
extensibility, composability, and usability than what is possible with
today's C++.

This tutorial will teach concepts from the ground up. We will begin
with an overview of the new features introduced by concepts and how
they will benefit C++ programmers. Then, we'll dive right into
concepts, building the core components of the C++ Standard (Template)
Library. We will see how these core components are more robust and
versatile than the equivalent components in today's C++. From there,
we will explore some of the more advanced features of concepts.
    """) | save

con_lib = Session(
    title="Evolving a C++ Library to C++0x Concepts", 
    short_title="Evolving to Concepts",
    start=thu[2],
    presenter=gregor,
    format='tutorial',
    track=dev,
    description=u"""
Concepts are a major addition to C++0x that make templates more
robust, more powerful, and easier to write and use. At their most
basic level, concepts provide a type system for templates.  Using
concepts, the C++ compiler is able to detect errors in the definition
and use of templates before they are instantiated.  One immediately
obvious benefit of this separate type-checking capability is a
dramatic improvement in error messages resulting from improper use of
templates. Look a little deeper and we find that concepts support an
entirely new programming paradigm, Generic Programming, enabling the
construction of a new breed of generic libraries that provide better
extensibility, composability, and usability than what is possible with
today's C++.

This tutorial will delve into the evolution of existing C++ libraries
to use concepts. We will discuss the translation of today's
documentation-only "concepts" into C++0x concepts and the introduction
of concepts into existing templates. Our focus throughout is on
evolving libraries without requiring extensive rewrites and without
breaking existing user code.
    """) | save

summer = Session(
    title="Boost and Google Summer of Code", 
    short_title="Summer of Code", 
    presenter=garland,
    start=fri[0],
    track=user,
    format='experience report',
    description=u"""
Google Summer of Code (SOC) is a program by Google to encourage students to 
develop open source code while providing a chance to be employed.  In 2006 
Boost became a mentoring organization for SOC.  As an organization, Boost was 
quite unprepared for the avalanche of interest in 2006: some 174 project 
proposals.  Ultimately, Boost mentored 10 projects, but it was a scramble to 
recruit mentors, review all the proposals, and correctly mentor the students.

This talk will cover:

- Basic overview of Google SOC and Boost Participation
- Overview of the 10 2006 SOC projects
- Results of 2006 Boost SOC projects
- Lessons learned from 2006
- An overview of Jeff's trip to the Googleplex to meet other SOC mentors
- A look ahead to SOC 2007

In addition to the talk the session will include time for questions and 
brainstorming about how the Boost Community can better support SOC in 2007 and 
beyond.
    """) | save

future = Session(
    title="Future of Boost", 
    short_title="Future of Boost", 
    presenter=garland,
    start=fri[1],
    track=dev,
    format='panel',
    description=u"""
Boost has a small group of moderators that keep the mailing list running 
including approving posts and moderation to keep the mailing list on-topic, 
respectful, and useful.  In addition, they administer internals of the 
website, source repository and other administrative machinery.  And last, but 
not least, the moderators also act as an informal executive overseeing 
committee to promote all things Boost.

In this session, each moderator will be given 5 minutes to say something about 
their vision of the future of Boost, but the majority of the session will be 
devoted to questions and proposals from the audience.  This is your chance to 
ask or propose absolutely anything about the direction of the Boost community. 
For example, why we don't adopt a particular policy, tool, or idea.
    """) | save

value = Session(
    title="Value-Based Programming",
    start=tue[0],
    track=user,
    duration=4*90,
    short_title="Value-Based", 
    presenters=(garland,henney),
    format='tutorial',
    level=beginner|intermediate,
    description=u"""
Value-based programming is one of the cornerstones of reliable software 
design.  Unfortunately, too little has been written about the tools and 
techniques to building solid value types. Further, there is no standard 
toolkit for writing new value types.  Boost has several of the elements, but 
they haven't been pulled together in a coherent way.  The goal of this all day 
session will be to educate developers on the best uses of value types and 
develop a roadmap of missing libraries that can be developed as part of Boost 
to support rapid value type development.

Targeted to the developer part of the conference the idea will be to try and 
then develop a best practices and a 'value-based programming roadmap'.  The 
idea is to work on figuring out what's missing from the 'value programmers 
toolbox' and how this might be rectified.  We'll be mining best practices from 
libraries like boost.any, boost.rational, boost.date_time, etc. As one 
example, the constrained_value template used in Boost.date_time (should be 
its own little library) allows for the simple definition of constrained 
numeric types.

To keep things concrete we'll use a couple of not yet built libraries 
(SafeInteger and Money) as examples in our discussion of value types.  We'll 
use these value types to motivate the requirements and overall design of the 
value programmers toolkit.

The day-long lecture/workshop will be divided into four 90 minute parts:

Part 1: Lecture Session: Introduction to Value Types
-  Henney on Value Types: Presentation on Value Types -- what they are, 
why they're useful, why they are different from objects, how they impact design
- Garland on available Value Type libraries: presentation on some of the 
currently available including constrained_value, Boost.operators, proposed 
boost_enum, etc.

Part 2: Workshop: Group attempt to create some new value type libraries
- Introduction of example value types 'SafeInt and Money'
- Brainstorming of interfaces for the value types

Part 3: Workshop: Analysis of new value types and needs for the value type toolkit
- Development of a list of commonalities among the value types
- Brainstorming of libraries that could be utilized in creation of value types

Part 4: Workshop: Documentation of Workshop Results
- Documentation of the 'value type library roadmap' (list of library tools 
that should be developed to support building of value types)
- Documentation of useful tools and techniques
    """) | save

proto = Session(
    title="Implementing Domain Specific Embedded Languages using Expression Templates and Boost.Proto", 
    short_title="Proto", 
    presenter=niebler,
    format='tutorial',
    start=thu[0],
    track=dev,
    level=advanced,
    description=u"""
Expression Templates are an advanced technique that C++ library
developers use to define embedded mini-languages that target specific
problem domains. The technique has been used to create hyper-efficient
and easy-to-use libraries for linear algebra as well as to define C++
parser generators with a readable syntax. But developing such a library
involves writing an inordinate amount of unreadable and unmaintainable
template mumbo-jumbo. Boost.Proto, a new library currently under
development, eases the development of domain-specific embedded languages
(DSELs). Use Proto to define the primitives of your mini-language and
let Proto handle the operator overloading and the construction of the
expression parse tree. Immediately evaluate the expression tree by
passing it a function object. Or transform the expression tree by
defining the meta-grammar of your mini-language, decorated with an
assortment of tree transforms provided by Proto or defined by you. Then
use the meta-grammar to give your users short and readable syntax errors
for invalid expressions! No more mumbo-jumbo -- an expression template
library developed with Proto is declarative and readable. Proto is a
DSEL for defining DSELs.

Proto was initially developed as a part of Boost.Xpressive. It is now
being used in the Spirit-2 rewrite (under development) and in another
future Boost DSEL library called Karma. Proto is the key to making these
three DSEL libraries play well together. It will eventually be proposed
as a stand-alone Boost library.
    """) | save

asl = Session(
    title="The Adobe Source Library: An approach to writing ADL-safe, generic libraries", 
    short_title="ASL", 
    presenter=marcus,
    start=thu[3],
    format='tutorial',
    track=dev,
    level=intermediate|advanced,
    description=u"""
The Adobe Source Library (ASL), http://opensource.adobe.com, is an open
source library extending boost with additional algorithms, data structures
and a user-interface development toolkit.
The ASL uses a set of conventions that can be used to produce
libraries that are safe to use in the presence of the C++ '03 argument
dependent lookup (ADL) language feature). The strategy aims to satisfy the
following criteria:

- Collision-safe:
	
  Functions in the ASL public API can be written to be callable as,
  for example, adobe::foo. However such functions are guaranteed not
  to be considered when making unqualified calls to foo, even from
  inside namespace adobe. In other words, such functions co-exist
  peacefully with present or future user, library, or third-party
  defined functions that happen to also be named foo.
	
- Customizable:
	
  Function (templates) in the ASL public API can be written so as to
  provide a "default" implementation, still callable as above and
  meeting the collision-safe criterion, while at the same time
  allowing the user or other parts of the library to provide custom
  implementations for their own types, in their own namespace.
	
Simply declaring functions in the library's namespace adobe isn't
collision-safe inside of the library. And the usual overloading or function
template specialization techniques violate collision-safety and have the
undesirable side-effect of forcing the user to define functions or
specializations in the library's namespace.
    """) | save
    
bgl = Session(
    title="Generic Programming and the Boost Graph Library", 
    short_title="BGL", 
    presenter=siek,
    format='tutorial',
    start=mon[0],
    duration=2*90,
    track=dev,
    level=intermediate,
    description=u"""
Many programming problems in diverse areas as Internet packet routing, molecular biology,
scientific computing, and telephone network design can be solved by using graph algorithms
and data-structures. Traditional approaches to implementing graph libraries
fail to provide enough flexibility, making them difficult to use in the context of a particular
application. Fortunately, Stepanov and Musser showed how flexibility can be achieved
without sacrificing performance using Generic Programming and demonstrated this
by implementing the Standard Template Library (STL). The Boost Graph Library (BGL) applies
the Generic Programming methodology to the graph domain and the result is a highly
flexible and efficient library for solving graph problems.

However, if you are unfamiliar with the generic programming paradigm, the
design of the BGL may seem odd and you may find it difficult to use.
In this tutorial we will become familiar with generic programming and its
underlying principles, see how these principles are applied in the BGL,
and learn the C++ template techniques used to implement generic libraries.
We will put the BGL to use in several programming problems and learn how
to take full advantage of its power and flexibility.

For developers interested in creating generic libraries, this tutorial will
provide a valuable example of how to apply generic programming in
a setting somewhat different from the classical sequence algorithms of
the STL.
    """) | save

python = Session(
    title="Implementing out-of-the-ordinary object models using Boost.Python    ", 
    short_title="Python object models", 
    presenter=shead,
    format='lecture',
    start=tue[3],
    track=dev,
    level=intermediate,
    attendee_background=u'assumes some prior knowledge of Boost.Python.',
    description=u"""
One mark of a good library is its ability to handle
out-of-the-ordinary use cases.  After several years observing
Boost.Python from afar, I set out in mid 2006 to see if it could
replace a large body of home-grown Python wrapping code
written for embedding in a 3D modeling and animation package. 
Along the way I developed a number of simple techniques dealing
with "real-world-messiness" that are the focus of the presentation,
including:

* Embedding Boost.Python wrappers in your executable (rather
  than loading them into Python)
* Mixing class-methods with non-intrusive methods (what to do
  when your Python object needs to differ slightly from its C++
  counterpart).
* Wrapping C++ template classes.
* Handling weakly-typed arguments and return-values in C++.
* Bypassing Boost.Python to implement "special" Python methods -
  __str__, __len__, etc.
* Module attributes
* And more!
    """) | save

drinks = Session(    
    title="Informal Gathering; Drinks.",
    schedule_note="Travelling companions welcome.",
    short_title="Drinks",
    format='social event',
    start=TimeBlock(start=datetime(2007,5,13,12+6,00), duration=0, conference=boostcon07) | save,
    description=u"""
Get to know your fellow Boosters and catch up with old friends.  Bring your
families and companions.
    """) | save
    
for s in Session.objects.all():
    print s
